# Implementation Plan - Download Organizer v3

## Goal Description
Fix `.rar` extraction error reported by the user (`Unknown archive format`).

## User Review Required
> [!IMPORTANT]
> RAR extraction requires an external tool like **WinRAR** or **7-Zip** to be installed on the system (and preferably in the PATH, though `patool` tries to find them). I will implement `patoolib` to bridge this. If the user has neither installed, the app will Log/Alert that external tools are missing, as strict standalone RAR extraction is complex due to licensing/binary requirements.

## Proposed Changes

### Logic Updates (`organizer.py`)
1.  **Dependencies**: Import `patoolib`.
2.  **RAR Handling**:
    - Detect `.rar` extension.
    - Call `patoolib.extract_archive(filepath, outdir=extract_path)`.
    - This supports RAR, 7z, and others better than `shutil`.
3.  **Error Handling**:
    - If `patoolib` fails (e.g., no backend found), show a specific error log: "Error: No RAR extractor found. Please install WinRAR or 7-Zip.".
    - Fallback: Move file to `OTROS/<filename>` (folder) or just `OTROS` root without extracting.

### Build
- Install `patool`.
- Build command: `pyinstaller --onefile --noconsole --icon=app_icon.ico --hidden-import patoolib --name="OrganizadorDescargas" organizer.py`

## Verification
- Attempt to create a mock rar if possible, or just verify the code structure.
- Rely on user testing for the actual RAR file they have.
