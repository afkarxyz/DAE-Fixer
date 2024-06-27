import customtkinter as ctk
import re
import os
from tkinter import filedialog, messagebox

class DAEFixer(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("DAE Fixer")
        self.geometry("500x400")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1)

        self.single_file_label = ctk.CTkLabel(self, text="Input File (Single Processing)")
        self.single_file_label.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="w")

        self.single_file_entry = ctk.CTkEntry(self, width=300)
        self.single_file_entry.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.single_file_browse = ctk.CTkButton(self, text="Browse", command=self.browse_single_file, width=100)
        self.single_file_browse.grid(row=1, column=1, padx=(0, 20), pady=(0, 10))

        self.directory_label = ctk.CTkLabel(self, text="Input Folder (Batch Processing)")
        self.directory_label.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="w")

        self.directory_entry = ctk.CTkEntry(self, width=300)
        self.directory_entry.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.directory_browse = ctk.CTkButton(self, text="Browse", command=self.browse_directory, width=100)
        self.directory_browse.grid(row=3, column=1, padx=(0, 20), pady=(0, 10))

        self.process_button = ctk.CTkButton(self, text="Process", command=self.process_files, width=100)
        self.process_button.grid(row=4, column=0, columnspan=2, padx=20, pady=20)

        self.progress_bar = ctk.CTkProgressBar(self, width=460)
        self.progress_bar.grid(row=5, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")
        self.progress_bar.set(0)

        self.output_text = ctk.CTkTextbox(self, width=460, height=150)
        self.output_text.grid(row=6, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="nsew")

    def browse_single_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("DAE files", "*.dae")])
        if file_path:
            self.single_file_entry.delete(0, ctk.END)
            self.single_file_entry.insert(0, file_path)

    def browse_directory(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.directory_entry.delete(0, ctk.END)
            self.directory_entry.insert(0, dir_path)

    def process_files(self):
        single_file = self.single_file_entry.get()
        directory = self.directory_entry.get()
        
        self.output_text.delete('1.0', ctk.END)
        self.progress_bar.set(0)
        
        files_to_process = []
        
        if single_file and single_file.endswith('.dae'):
            files_to_process.append(single_file)
        
        if directory:
            for root, _, files in os.walk(directory):
                files_to_process.extend([os.path.join(root, f) for f in files if f.endswith('.dae')])
        
        if not files_to_process:
            self.output_text.insert(ctk.END, "Please select a valid .dae file or directory containing .dae files.\n")
            return
        
        total_files = len(files_to_process)
        for i, file in enumerate(files_to_process):
            self.process_file(file)
            self.progress_bar.set((i + 1) / total_files)
            self.update_idletasks()
        
        self.output_text.insert(ctk.END, f"Processed {total_files} file(s).\n")
        
        # Show completion pop-up
        messagebox.showinfo("Process Complete", f"Successfully processed {total_files} file(s).")

    def process_file(self, input_file):
        output_file = os.path.splitext(input_file)[0] + '_output.dae'
        try:
            with open(input_file, 'r') as f:
                content = f.read()

            pattern = r'<texture[^>]*>.*?</texture>|<texture[^>]*\s*/>'
            
            def replace_texture(match):
                return ''

            cleaned_content = re.sub(pattern, replace_texture, content, flags=re.DOTALL)

            with open(output_file, 'w') as f:
                f.write(cleaned_content)

            self.output_text.insert(ctk.END, f"Processed: {input_file}\n")
        except Exception as e:
            self.output_text.insert(ctk.END, f"Error processing {input_file}: {str(e)}\n")

if __name__ == "__main__":
    app = DAEFixer()
    app.mainloop()
