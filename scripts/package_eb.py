import os
import zipfile

def package_backend():
    backend_dir = r"d:\Development Drive\JanSetu\backend"
    output_zip = r"d:\Development Drive\JanSetu\jansetu-backend-eb.zip"

    exclude_dirs = {"venv", ".venv", "__pycache__", ".pytest_cache", "tests", "storage", ".git"}
    exclude_files = {".env", "jansetu.db"}

    print(f"Creating Elastic Beanstalk bundle: {output_zip}")
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(backend_dir):
            # Prune excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                if file in exclude_files or file.endswith(".pyc") or file.endswith(".log"):
                    continue

                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, backend_dir)
                zf.write(abs_path, rel_path)
                print(f"  Added: {rel_path}")

    size_mb = os.path.getsize(output_zip) / (1024 * 1024)
    print(f"\nBundle created successfully! Size: {size_mb:.2f} MB")
    print(f"File location: {output_zip}")

if __name__ == "__main__":
    package_backend()
