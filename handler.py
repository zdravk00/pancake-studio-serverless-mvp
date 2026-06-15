import os
import sys
import subprocess
import boto3
import tempfile
from pathlib import Path

S3_BUCKET = os.environ.get("S3_BUCKET_NAME")
AWS_REGION = os.environ.get("AWS_REGION", "eu-central-1")

def handler(event, context):
    """RunPod Serverless Einstiegspunkt"""
    try:
        input_key = event.get("input_key")
        output_key = event.get("output_key")
        
        if not input_key or not output_key:
            return {"status": "error", "message": "input_key and output_key required"}
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            input_local = tmp / "input.flac"
            
            # Download von S3
            s3 = boto3.client("s3", region_name=AWS_REGION)
            s3.download_file(S3_BUCKET, input_key, str(input_local))
            
            # Demucs ausführen
            out_dir = tmp / "separated"
            out_dir.mkdir()
            cmd = [sys.executable, "-m", "demucs", "--two-stems", "vocals", "-o", str(out_dir), str(input_local)]
            subprocess.run(cmd, check=True)
            
            # vocals.wav suchen und in output.flac umwandeln
            vocals = list(out_dir.rglob("vocals.wav"))[0]
            output_local = tmp / "output.flac"
            subprocess.run(["ffmpeg", "-y", "-i", str(vocals), "-acodec", "flac", str(output_local)], check=True)
            
            # Upload nach S3
            s3.upload_file(str(output_local), S3_BUCKET, output_key)
        
        return {"status": "success", "output_key": output_key}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}