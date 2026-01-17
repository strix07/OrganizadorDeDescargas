import os
import shutil
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from PIL import Image
from datetime import datetime
import zipfile
import tarfile
import patoolib

# Configuration
DOWNLOADS_FOLDER = os.path.expanduser('~/Downloads')
LOG_FILE = os.path.join(os.path.expanduser('~/Desktop'), 'organizer_log.txt')

CATEGORIES = {
    'IMAGENES': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg', '.ico', '.tiff'],
    'DOCUMENTOS': ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pdf', '.txt', '.csv', '.rtf', '.odt', '.ods', '.odp'],
    'COMPRESSED': ['.zip', '.tar', '.gz', '.7z', '.rar']
}

def log_error(msg):
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(f"[{datetime.now()}] {msg}\n")
    except:
        pass

def get_category(extension):
    ext = extension.lower()
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return 'OTROS'

class OrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Organizador de Descargas")
        self.root.geometry("400x200")
        self.root.resizable(False, False)

        self.style = ttk.Style()
        self.style.configure("TButton", font=("Helvetica", 12), padding=10)
        self.style.configure("TLabel", font=("Helvetica", 10))

        frame = ttk.Frame(root, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        self.label = ttk.Label(frame, text="Presiona el botón para organizar tus descargas.")
        self.label.pack(pady=(0, 20))

        self.organize_btn = ttk.Button(frame, text="Organizar", command=self.start_organization)
        self.organize_btn.pack(pady=10)

        self.progress = ttk.Progressbar(frame, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.progress.pack(pady=20)

    def start_organization(self):
        self.organize_btn.config(state=tk.DISABLED)
        self.progress['value'] = 0
        self.label.config(text="Organizando...")
        
        thread = threading.Thread(target=self.run_process)
        thread.start()

    def run_process(self):
        try:
            self.organize_files()
            self.check_misplaced_files()
            self.update_ui_complete()
        except Exception as e:
            log_error(f"Critical Process Error: {e}")
            self.update_ui_error(str(e))

    def organize_files(self):
        # Create categories folders if they don't exist
        for folder in ['IMAGENES', 'DOCUMENTOS', 'OTROS']:
            path = os.path.join(DOWNLOADS_FOLDER, folder)
            os.makedirs(path, exist_ok=True)

        files = [f for f in os.listdir(DOWNLOADS_FOLDER) if os.path.isfile(os.path.join(DOWNLOADS_FOLDER, f))]
        total_files = len(files)
        
        for i, filename in enumerate(files):
            if total_files > 0:
                progress_val = (i / total_files) * 50
            else:
                progress_val = 50
            self.update_progress(progress_val)

            filepath = os.path.join(DOWNLOADS_FOLDER, filename)
            _, ext = os.path.splitext(filename)
            category = get_category(ext)

            target_folder = 'OTROS'
            
            if category == 'IMAGENES':
                target_folder = 'IMAGENES'
                self.safe_move_image(filepath, os.path.join(DOWNLOADS_FOLDER, target_folder))
                continue
            elif category == 'DOCUMENTOS':
                target_folder = 'DOCUMENTOS'
            elif category == 'COMPRESSED':
                self.handle_compressed(filepath, filename)
                continue
            
            target_path = os.path.join(DOWNLOADS_FOLDER, target_folder, filename)
            self.safe_move(filepath, target_path)

    def handle_compressed(self, filepath, filename):
        name_no_ext = os.path.splitext(filename)[0]
        extract_path = os.path.join(DOWNLOADS_FOLDER, 'OTROS', name_no_ext)
        os.makedirs(extract_path, exist_ok=True)
        
        try:
            # Check extension logic
            lower_name = filename.lower()
            
            if lower_name.endswith('.zip'):
                with zipfile.ZipFile(filepath, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
            elif lower_name.endswith('.tar') or lower_name.endswith('.gz'):
                 with tarfile.open(filepath, 'r:*') as tar_ref:
                    tar_ref.extractall(extract_path)
            elif lower_name.endswith('.rar') or lower_name.endswith('.7z'):
                # Use patool for RAR and 7z
                # Patool raises patoolib.util.PatoolError if tool not found
                patoolib.extract_archive(filepath, outdir=extract_path)
            else:
                # Fallback for others
                shutil.unpack_archive(filepath, extract_path)
            
            # If successful, remove original
            os.remove(filepath)
            
        except patoolib.util.PatoolError as e:
            log_error(f"External Tool Error for {filename}: {e}. Ensure WinRAR or 7-Zip is installed.")
            # Move manually to folder so user can handle it
            target_path = os.path.join(DOWNLOADS_FOLDER, 'OTROS', filename)
            self.safe_move(filepath, target_path)
            # Remove empty extract path if empty
            if os.path.exists(extract_path) and not os.listdir(extract_path):
                os.rmdir(extract_path)
                
        except Exception as e:
            log_error(f"Error extracting {filename}: {e}")
            target_path = os.path.join(DOWNLOADS_FOLDER, 'OTROS', filename)
            self.safe_move(filepath, target_path)

    def safe_move_image(self, src, folder_path):
        try:
            ctime = os.path.getctime(src)
            dt_obj = datetime.fromtimestamp(ctime)
            new_name = dt_obj.strftime("IMG_%Y%m%d_%H%M%S")
            _, ext = os.path.splitext(src)
            new_filename = f"{new_name}{ext}"
            
            dst = os.path.join(folder_path, new_filename)
            
            counter = 1
            base, extension = os.path.splitext(dst)
            while os.path.exists(dst):
                dst = f"{base}_{counter}{extension}"
                counter += 1
                
            shutil.move(src, dst)
        except Exception as e:
            log_error(f"Error moving image {src}: {e}")
            # Fallback
            filename = os.path.basename(src)
            self.safe_move(src, os.path.join(folder_path, filename))

    def check_misplaced_files(self):
        folders_to_check = ['IMAGENES', 'DOCUMENTOS', 'OTROS']
        
        for folder_name in folders_to_check:
            folder_path = os.path.join(DOWNLOADS_FOLDER, folder_name)
            if not os.path.exists(folder_path):
                continue
                
            files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            
            for i, filename in enumerate(files):
                filepath = os.path.join(folder_path, filename)
                _, ext = os.path.splitext(filename)
                category = get_category(ext)
                
                correct_folder = ''
                if category == 'IMAGENES' and folder_name != 'IMAGENES':
                    correct_folder = 'IMAGENES'
                elif category == 'DOCUMENTOS' and folder_name != 'DOCUMENTOS':
                    correct_folder = 'DOCUMENTOS'
                elif category == 'COMPRESSED':
                    self.handle_compressed(filepath, filename)
                    continue
                elif category == 'OTROS' and folder_name != 'OTROS':
                     correct_folder = 'OTROS'

                if correct_folder:
                    target_dir = os.path.join(DOWNLOADS_FOLDER, correct_folder)
                    if correct_folder == 'IMAGENES':
                        self.safe_move_image(filepath, target_dir)
                    else:
                        target_path = os.path.join(target_dir, filename)
                        self.safe_move(filepath, target_path)
            
            if folder_name == 'IMAGENES':
                self.rename_existing_images(folder_path)

        self.update_progress(95)

    def rename_existing_images(self, folder_path):
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        for filename in files:
            filepath = os.path.join(folder_path, filename)
            try:
                ctime = os.path.getctime(filepath)
                dt_obj = datetime.fromtimestamp(ctime)
                new_basename = dt_obj.strftime("IMG_%Y%m%d_%H%M%S")
                _, ext = os.path.splitext(filename)
                
                if filename.startswith(new_basename):
                    continue
                
                new_full_name = f"{new_basename}{ext}"
                dst = os.path.join(folder_path, new_full_name)
                
                if os.path.abspath(filepath) == os.path.abspath(dst):
                     continue
                     
                counter = 1
                base, extension = os.path.splitext(dst)
                while os.path.exists(dst):
                    dst = f"{base}_{counter}{extension}"
                    counter += 1
                
                os.rename(filepath, dst)
            except Exception as e:
                log_error(f"Error renaming existing image {filename}: {e}")

    def safe_move(self, src, dst):
        try:
           if os.path.abspath(src) == os.path.abspath(dst):
               return

           if os.path.exists(dst):
               base, ext = os.path.splitext(dst)
               counter = 1
               while os.path.exists(f"{base}_{counter}{ext}"):
                   counter += 1
               dst = f"{base}_{counter}{ext}"
           shutil.move(src, dst)
        except Exception as e:
            log_error(f"Error moving {src}: {e}")

    def update_progress(self, val):
        self.root.after(0, lambda: self.progress.config(value=val))

    def update_ui_complete(self):
        self.root.after(0, lambda: self.label.config(text="¡Organización Completada!"))
        self.root.after(0, lambda: self.progress.config(value=100))
        self.root.after(0, lambda: messagebox.showinfo("Éxito", "La carpeta de descargas ha sido organizada."))
        self.root.after(0, lambda: self.organize_btn.config(state=tk.NORMAL))

    def update_ui_error(self, error_msg):
        self.root.after(0, lambda: self.label.config(text="Error"))
        self.root.after(0, lambda: messagebox.showerror("Error", f"Ocurrió un error. Ver log en escritorio."))
        self.root.after(0, lambda: self.organize_btn.config(state=tk.NORMAL))

if __name__ == "__main__":
    root = tk.Tk()
    try:
        if os.path.exists('app_icon.ico'):
             root.iconbitmap('app_icon.ico')
    except:
        pass

    app = OrganizerApp(root)
    root.mainloop()
