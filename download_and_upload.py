import os
import requests

# ---- Configuration ----
ON_PREM_URL = "https://artifactory.wellsfargo.com/artifactory"  
ON_PREM_REPO = "maven-wf-local"
ON_PREM_USER = "K125710"
ON_PREM_PASSWORD = "<your_onprem_password_or_token>"

SAAS_URL = "https://wffrogclnp00.jfrog.io/artifactory"
SAAS_REPO = "prod-devin-java"
SAAS_USER = "EBSSH_JFROG_SVC_PRD"
SAAS_PASSWORD = "<your_jfrog_token>"

ARTIFACTS = [
    "com/wellsfargo/ebssh/orchestra/loglib-logback-spring-starter/3.17.0/loglib-logback-spring-starter-3.17.0.jar"
]

def download_to_cwd(artifact_path: str) -> str:
    """Download artifact and save it to the current working directory."""
    url = f"{ON_PREM_URL}/{ON_PREM_REPO}/{artifact_path}"
    print(f"[INFO] Downloading from: {url}")

    with requests.get(url, auth=(ON_PREM_USER, ON_PREM_PASSWORD), stream=True, verify=False) as r:
        print(f"[INFO] Download status: {r.status_code}")
        r.raise_for_status()

        filename = os.path.basename(artifact_path)
        local_path = os.path.join(os.getcwd(), filename)

        with open(local_path, "wb") as f:
            for chunk in r.iter_content(8192):
                if chunk:
                    f.write(chunk)

    size = os.path.getsize(local_path)
    print(f"[INFO] Saved to {local_path} ({size} bytes)")
    return local_path


def upload_file(artifact_path: str, local_file: str) -> None:
    """Upload local file to SaaS Artifactory."""
    url = f"{SAAS_URL}/{SAAS_REPO}/{artifact_path}"
    size = os.path.getsize(local_file)
    headers = {
        "Content-Type": "application/octet-stream",
        "Content-Length": str(size)
    }

    print(f"[INFO] Uploading {local_file} -> {url} ({size} bytes)")
    with open(local_file, "rb") as f:
        r = requests.put(url, data=f, headers=headers, auth=(SAAS_USER, SAAS_PASSWORD), verify=False)

    print(f"[INFO] Upload status: {r.status_code}")
    r.raise_for_status()
    print(f"[INFO] Uploaded OK")


if __name__ == "__main__":
    print("[INFO] Starting migration of dependencies...")
    for artifact in ARTIFACTS:
        try:
            print(f"[INFO] Transferring {artifact}...")
            local_path = download_to_cwd(artifact)
            print(f"[INFO] Downloaded {artifact} to {local_path}")
            upload_file(artifact, local_path)
            print(f"[INFO] Uploaded {artifact} to {SAAS_URL}/{SAAS_REPO}/{artifact}")
            print(f"[SUCCESS] Transferred {artifact}")
        except Exception as e:
            print(f"[ERROR] Failed to transfer {artifact}: {e}")
    
# pip install requests