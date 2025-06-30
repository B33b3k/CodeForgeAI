import subprocess
import tempfile
import os

SUPPORTED_LANGS = {"python", "py"}

class ExecuteAgent:
    def run(self, language: str, clean_code: str) -> str:
        lang = language.lower()
        if lang not in SUPPORTED_LANGS:
            return f"Execution not supported for language: {language}"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(clean_code)
            temp_path = f.name
        try:
            result = subprocess.run(["python3", temp_path], capture_output=True, text=True, timeout=10)
            output = result.stdout + ("\n" + result.stderr if result.stderr else "")
        except Exception as e:
            output = str(e)
        finally:
            os.remove(temp_path)
        return output.strip()
