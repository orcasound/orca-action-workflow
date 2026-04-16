# importing general Python libraries
import datetime as dt
import pytz
import json
import argparse
import boto3
from botocore.exceptions import ClientError
import tempfile

# importing orcasound_noise libraries
from orcasound_noise.pipeline.pipeline import NoiseAnalysisPipeline
from orcasound_noise.utils import Hydrophone
from orcasound_noise.utils.file_connector import S3FileConnector

# Bookmarking
class Bookmark:
    def __init__(self, hydrophone: Hydrophone, last_processed: dt.datetime = None):
        self.bookmark_path = f"s3://{hydrophone.value.save_bucket}/{hydrophone.value.bookmark_folder}/{hydrophone.value.name}_bookmark.json"
        self.hydrophone = hydrophone.value.name
        self.bucket = hydrophone.value.save_bucket
        self.folder = hydrophone.value.bookmark_folder
        self.last_processed = last_processed
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.client = boto3.client('s3')
        self.temp_bookmark_path = f'{self.tmp_dir.name}/{self.hydrophone}_bookmark.json'
        self.s3_bookmark_path = f'{self.folder}/{self.hydrophone}_bookmark.json'
    
    def update(self, new_time: dt.datetime):
        self.last_processed = new_time
        try:
            with open(self.temp_bookmark_path, 'w') as f:
                json.dump({'last_processed': self.last_processed.isoformat()}, f)
            self.client.upload_file(self.temp_bookmark_path, self.bucket, self.s3_bookmark_path)
            self.tmp_dir.cleanup()
        except FileNotFoundError as e:
            print(f"Error updating bookmark: {e}")
    
    def load(self):
        try:
            self.client.head_object(Bucket=self.bucket, Key=self.s3_bookmark_path)
            self.client.download_file(self.bucket, self.s3_bookmark_path, self.temp_bookmark_path)
            with open(self.temp_bookmark_path, 'r') as f:
                data = json.load(f)
                self.last_processed = dt.datetime.fromisoformat(data['last_processed'])
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                print(f"No existing bookmark found for {self.hydrophone}. Starting fresh.")
                self.last_processed = None

def process_upload_psd(start_time: dt.datetime, end_time: dt.datetime, 
                       hydrophone: Hydrophone, bookmark: Bookmark, file_connector: S3FileConnector):
    
    """
    Process and upload PSD parquet files for a given hydrophone and time range.
    Args:
        start_time (dt.datetime): Start time for processing.
        end_time (dt.datetime): End time for processing.
        hydrophone (Hydrophone): Hydrophone object containing metadata.
        bookmark (Bookmark): Bookmark object for tracking last processed time.
        file_connector (S3FileConnector): File connector for S3 interactions.
    """
    pipeline = NoiseAnalysisPipeline(hydrophone,
                                     delta_f=1, bands=12,
                                     delta_t=1, mode='safe',
                                     )
    
    psd_path, bb_path = pipeline.generate_parquet_file(start_time, 
                                        end_time, 
                                        upload_to_s3=True,
                                        partitioning=True)
    
    bookmark.update(end_time)

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Process hydrophone audio data and generate PSD parquet files.')
    parser.add_argument('--hydrophone', 
                       type=str, 
                       default='bush_point',
                       choices=[h.value.name for h in Hydrophone][1:],
                       help='Hydrophone location to process')
    
    args = parser.parse_args()
    hydrophone = Hydrophone[args.hydrophone.upper()]
    
    pst_fixed = dt.timezone(dt.timedelta(hours=-8), name="PST")
    now = dt.datetime.now(pst_fixed)

    # Load Bookmark
    bookmark = Bookmark(hydrophone)
    bookmark.load()
    start_time = bookmark.last_processed or (now - dt.timedelta(hours=1))
    # if the bookmark is older than 6 hours, reset to 1 hour ago to avoid processing large amounts of data at once
    if start_time < now - dt.timedelta(hours=6):
        start_time = now - dt.timedelta(hours=1)
    end_time = now - dt.timedelta(minutes=5)  # buffer to ensure all data is available

    file_connector = S3FileConnector(hydrophone)
    process_upload_psd(start_time, end_time, hydrophone, bookmark, file_connector)

if __name__ == '__main__':
    main()