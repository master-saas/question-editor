import os
import json
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import shutil

class QuestionEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Question JSON Editor")
        self.root.geometry("1100x850")
        
        self.output_dir = os.getcwd()
        self.year = os.path.basename(self.output_dir)
        self.questions_dir = os.path.join(self.output_dir, "questions")
        
        if not os.path.exists(self.questions_dir):
            messagebox.showerror("Error", f"Questions folder not found: {self.questions_dir}\nRun this script inside the output/year folder")
            root.destroy()
            return
        
        self.folders = sorted([f for f in os.listdir(self.questions_dir) if os.path.isdir(os.path.join(self.questions_dir, f))], key=lambda x: (int(re.match(r'^(\d+)', x).group(1)) if re.match(r'^(\d+)', x) else 9999, x))
        self.current_index = 0
        
        self.create_ui()
        self.load_current_question()
        self.root.bind("<Control-s>", lambda e: self.save_current_question())
    
    def create_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.tab_questions = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_questions, text="Question Editor")
        
        self.create_question_tab()
    
    def create_question_tab(self):
        leftPane = ttk.PanedWindow(self.tab_questions, orient="horizontal")
        leftPane.pack(fill="both", expand=True)
        
        left_frame = ttk.Frame(leftPane, width=550)
        leftPane.add(left_frame, weight=1)
        
        right_frame = ttk.Frame(leftPane)
        leftPane.add(right_frame)
        
        nav_top_frame = ttk.Frame(left_frame)
        nav_top_frame.pack(anchor="w", pady=(0, 10))
        ttk.Button(nav_top_frame, text="< Previous", command=self.go_previous).pack(side="left", padx=5)
        
        self.entry_jump = ttk.Entry(nav_top_frame, width=10, justify="center")
        self.entry_jump.pack(side="left", padx=5)
        self.entry_jump.bind("<FocusOut>", self.on_jump_focus_out)
        self.entry_jump.bind("<Return>", lambda e: self.root.focus_set())
        
        ttk.Button(nav_top_frame, text="Next >", command=self.go_next).pack(side="left", padx=5)
        
        self.lbl_folder = ttk.Label(left_frame, text="", font=("Arial", 12, "bold"))
        self.lbl_folder.pack(anchor="w")
        
        fields_frame = ttk.LabelFrame(left_frame, text="Fields")
        fields_frame.pack(fill="both", expand=True, pady=10)
        
        row = 0
        ttk.Label(fields_frame, text="Title:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.entry_title_q = ttk.Entry(fields_frame, width=50)
        self.entry_title_q.grid(row=row, column=1, sticky="ew", padx=5, pady=3)
        
        row += 1
        ttk.Label(fields_frame, text="Index:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.entry_index = ttk.Entry(fields_frame, width=15)
        self.entry_index.grid(row=row, column=1, sticky="w", padx=5, pady=3)
        
        row += 1
        ttk.Label(fields_frame, text="Year:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.entry_year_q = ttk.Entry(fields_frame, width=15)
        self.entry_year_q.grid(row=row, column=1, sticky="w", padx=5, pady=3)
        
        row += 1
        ttk.Label(fields_frame, text="Language:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.combo_language = ttk.Combobox(fields_frame, values=["ingles", "espanhol", ""], width=15)
        self.combo_language.grid(row=row, column=1, sticky="w", padx=5, pady=3)
        
        row += 1
        ttk.Label(fields_frame, text="Discipline:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.combo_discipline = ttk.Combobox(fields_frame, values=["linguagens", "ciencias-humanas", "ciencias-natureza", "matematica"], width=20)
        self.combo_discipline.grid(row=row, column=1, sticky="w", padx=5, pady=3)
        
        row += 1
        ttk.Label(fields_frame, text="Context:").grid(row=row, column=0, sticky="nw", padx=5, pady=3)
        self.text_context = tk.Text(fields_frame, width=50, height=10)
        self.text_context.grid(row=row, column=1, sticky="nsew", padx=5, pady=3)
        
        row += 1
        ttk.Label(fields_frame, text="Alternatives Introduction:").grid(row=row, column=0, sticky="nw", padx=5, pady=3)
        self.text_alt_intro = tk.Text(fields_frame, width=50, height=4)
        self.text_alt_intro.grid(row=row, column=1, sticky="ew", padx=5, pady=3)
        
        row += 1
        ttk.Button(fields_frame, text="Remove Line Breaks", command=self.remove_alt_intro_line_breaks).grid(row=row, column=1, sticky="w", padx=5, pady=3)
        
        row += 1
        ttk.Label(fields_frame, text="Correct Alternative:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.combo_correct = ttk.Combobox(fields_frame, values=["A", "B", "C", "D", "E"], width=10)
        self.combo_correct.grid(row=row, column=1, sticky="w", padx=5, pady=3)
        
        fields_frame.columnconfigure(1, weight=1)
        
        alts_paned = ttk.PanedWindow(left_frame, orient="horizontal")
        alts_paned.pack(fill="both", expand=True, pady=10)
        
        alts_entry_frame = ttk.Frame(alts_paned)
        alts_paned.add(alts_entry_frame, weight=1)
        
        alts_frame = ttk.LabelFrame(alts_entry_frame, text="Alternatives (A-E)")
        alts_frame.pack(fill="both", expand=True)
        
        self.alt_entries = {}
        letters = ["A", "B", "C", "D", "E"]
        for i, letter in enumerate(letters):
            ttk.Label(alts_frame, text=f"{letter}:").grid(row=i, column=0, sticky="w", padx=5, pady=3)
            entry = ttk.Entry(alts_frame, width=35)
            entry.grid(row=i, column=1, sticky="ew", padx=5, pady=3)
            self.alt_entries[letter] = entry
        
        alts_frame.columnconfigure(1, weight=1)
        
        alts_parse_frame = ttk.Frame(alts_paned)
        alts_paned.add(alts_parse_frame)
        
        ttk.Label(alts_parse_frame, text="Alternatives Parse").pack()
        
        self.text_alts_parse = tk.Text(alts_parse_frame, width=30, height=8)
        self.text_alts_parse.pack(fill="both", expand=True, padx=5, pady=5)
        
        ttk.Button(alts_parse_frame, text="Parse", command=self.parse_alternatives).pack(pady=5)
        
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill="x", pady=10)
        ttk.Button(btn_frame, text="Save", command=self.save_current_question).pack(side="left", padx=5)
        
        img_frame = ttk.LabelFrame(right_frame, text="Images (double-click to add to context)")
        img_frame.pack(fill="both", expand=True)
        
        img_list_frame = ttk.Frame(img_frame)
        img_list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.img_listbox = tk.Listbox(img_list_frame, height=15, selectmode="single")
        self.img_listbox.pack(side="left", fill="both", expand=True)
        self.img_listbox.bind('<<ListboxSelect>>', self.on_image_select)
        self.img_listbox.bind('<Double-Button-1>', self.on_image_double_click)
        
        scrollbar = ttk.Scrollbar(img_list_frame, orient="vertical", command=self.img_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.img_listbox.config(yscrollcommand=scrollbar.set)
        
        img_btn_frame = ttk.Frame(img_frame)
        img_btn_frame.pack(pady=5)
        ttk.Button(img_btn_frame, text="Add Image", command=self.add_image).pack(side="left", padx=2)
        ttk.Button(img_btn_frame, text="Remove", command=self.remove_image).pack(side="left", padx=2)
        ttk.Button(img_btn_frame, text="Replace", command=self.replace_image).pack(side="left", padx=2)
        
        img_order_frame = ttk.Frame(img_frame)
        img_order_frame.pack(pady=5)
        ttk.Button(img_order_frame, text="Move Up", command=self.move_image_up).pack(side="left", padx=2)
        ttk.Button(img_order_frame, text="Move Down", command=self.move_image_down).pack(side="left", padx=2)
        
        self.img_preview_label = ttk.Label(img_frame, text="Select image to preview")
        self.img_preview_label.pack(pady=10)
        
        self.current_image = None
        self.current_images = []
    
    def get_current_folder(self):
        return self.folders[self.current_index]
    
    def get_question_index(self):
        index = self.entry_index.get()
        if index.isdigit():
            return int(index)
        folder = self.get_current_folder()
        for c in folder:
            if c.isdigit():
                return int(''.join([d for d in folder if d.isdigit()]))
        return 1
    
    def load_current_question(self):
        folder = self.get_current_folder()
        self.lbl_folder.config(text=folder)
        self.entry_jump.delete(0, tk.END)
        self.entry_jump.insert(0, self.current_index + 1)
        
        details_path = os.path.join(self.questions_dir, folder, "details.json")
        if not os.path.exists(details_path):
            messagebox.showerror("Error", f"details.json not found in {folder}")
            return
        
        with open(details_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self.entry_title_q.delete(0, tk.END)
        self.entry_title_q.insert(0, data.get("title", ""))
        self.entry_index.delete(0, tk.END)
        self.entry_index.insert(0, str(data.get("index", "")))
        self.entry_year_q.delete(0, tk.END)
        self.entry_year_q.insert(0, str(data.get("year", "")))
        
        lang = data.get("language", "") or ""
        if lang not in self.combo_language['values']:
            lang = ""
        self.combo_language.set(lang)
        
        disc = data.get("discipline", "") or ""
        if disc not in self.combo_discipline['values']:
            disc = ""
        self.combo_discipline.set(disc)
        
        self.text_context.delete("1.0", tk.END)
        self.text_context.insert("1.0", data.get("context", ""))
        
        self.text_alt_intro.delete("1.0", tk.END)
        self.text_alt_intro.insert("1.0", data.get("alternativesIntroduction", ""))
        
        correct = data.get("correctAlternative", "") or ""
        if correct not in self.combo_correct['values']:
            correct = ""
        self.combo_correct.set(correct)
        
        for letter in ["A", "B", "C", "D", "E"]:
            entry = self.alt_entries[letter]
            entry.delete(0, tk.END)
            alt_text = ""
            for alt in data.get("alternatives", []):
                if alt.get("letter") == letter:
                    alt_text = alt.get("text", "")
            entry.insert(0, alt_text)
        
        self.load_folder_images()
    
    def load_folder_images(self):
        folder = self.get_current_folder()
        folder_path = os.path.join(self.questions_dir, folder)
        
        self.current_images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        self.current_images.sort()
        
        self.img_listbox.delete(0, tk.END)
        for img in self.current_images:
            self.img_listbox.insert(tk.END, img)
        
        self.img_preview_label.config(text=f"{len(self.current_images)} images")
        self.img_preview_label.image = None
    
    def parse_alternatives(self):
        text = self.text_alts_parse.get("1.0", tk.END).strip()
        if not text:
            messagebox.showinfo("Info", "No text to parse")
            return
        
        lines = text.split("\n")
        
        for letter in ["A", "B", "C", "D", "E"]:
            self.alt_entries[letter].delete(0, tk.END)
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line and line[0] in "ABCDE":
                letter = line[0]
                rest = line[1:].strip()
                
                if rest and rest[0] in ". ":
                    rest = rest[1:].strip()
                
                if letter in self.alt_entries:
                    self.alt_entries[letter].insert(0, rest)
        
        self.text_alts_parse.delete("1.0", tk.END)
    
    def remove_alt_intro_line_breaks(self):
        current = self.text_alt_intro.get("1.0", tk.END)
        cleaned = current.replace("\n", "").strip()
        self.text_alt_intro.delete("1.0", tk.END)
        self.text_alt_intro.insert("1.0", cleaned)
    
    def on_image_select(self, event):
        selection = self.img_listbox.curselection()
        if selection:
            idx = selection[0]
            folder = self.get_current_folder()
            folder_path = os.path.join(self.questions_dir, folder)
            img_path = os.path.join(folder_path, self.current_images[idx])
            self.preview_image(img_path)
    
    def on_image_double_click(self, event):
        selection = self.img_listbox.curselection()
        if selection:
            idx = selection[0]
            img_name = self.current_images[idx]
            markdown_ref = f"![]({img_name})"
            
            self.text_context.insert(tk.END, "\n" + markdown_ref)
    
    def preview_image(self, path):
        if not os.path.exists(path):
            self.img_preview_label.config(text="Image not found")
            return
        
        try:
            img = Image.open(path)
            img.thumbnail((400, 300))
            self.current_image = ImageTk.PhotoImage(img)
            self.img_preview_label.config(image=self.current_image, text="")
        except Exception as e:
            self.img_preview_label.config(text=f"Error: {e}")
    
    def add_image(self):
        folder = self.get_current_folder()
        folder_path = os.path.join(self.questions_dir, folder)
        
        filename = filedialog.askopenfilename(title="Add Image", filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.bmp")])
        if not filename:
            return
        
        new_name = f"image_temp_{len(self.current_images) + 1}.png"
        dest_path = os.path.join(folder_path, new_name)
        
        shutil.copy2(filename, dest_path)
        self.load_folder_images()
    
    def remove_image(self):
        selection = self.img_listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Select an image to remove")
            return
        
        idx = selection[0]
        img_name = self.current_images[idx]
        
        if messagebox.askyesno("Confirm", f"Remove {img_name}?"):
            folder = self.get_current_folder()
            folder_path = os.path.join(self.questions_dir, folder)
            img_path = os.path.join(folder_path, img_name)
            os.remove(img_path)
            self.load_folder_images()
    
    def replace_image(self):
        selection = self.img_listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Select an image to replace")
            return
        
        filename = filedialog.askopenfilename(title="Replace Image", filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.bmp")])
        if not filename:
            return
        
        folder = self.get_current_folder()
        folder_path = os.path.join(self.questions_dir, folder)
        
        shutil.copy2(filename, os.path.join(folder_path, f"image_temp_replace.png"))
        self.load_folder_images()
    
    def move_image_up(self):
        selection = self.img_listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Select an image to move")
            return
        
        idx = selection[0]
        if idx == 0:
            return
        
        folder = self.get_current_folder()
        folder_path = os.path.join(self.questions_dir, folder)
        
        img_name = self.current_images[idx]
        new_idx = idx - 1
        new_name = self.current_images[new_idx]
        
        temp_name = f"image_temp_swap.png"
        
        os.rename(os.path.join(folder_path, img_name), os.path.join(folder_path, temp_name))
        os.rename(os.path.join(folder_path, new_name), os.path.join(folder_path, img_name))
        os.rename(os.path.join(folder_path, temp_name), os.path.join(folder_path, new_name))
        
        self.load_folder_images()
        self.img_listbox.selection_set(new_idx)
    
    def move_image_down(self):
        selection = self.img_listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Select an image to move")
            return
        
        idx = selection[0]
        if idx >= len(self.current_images) - 1:
            return
        
        folder = self.get_current_folder()
        folder_path = os.path.join(self.questions_dir, folder)
        
        img_name = self.current_images[idx]
        new_idx = idx + 1
        new_name = self.current_images[new_idx]
        
        temp_name = f"image_temp_swap.png"
        
        os.rename(os.path.join(folder_path, img_name), os.path.join(folder_path, temp_name))
        os.rename(os.path.join(folder_path, new_name), os.path.join(folder_path, img_name))
        os.rename(os.path.join(folder_path, temp_name), os.path.join(folder_path, new_name))
        
        self.load_folder_images()
        self.img_listbox.selection_set(new_idx)
    
    def save_current_question(self):
        folder = self.get_current_folder()
        details_path = os.path.join(self.questions_dir, folder, "details.json")
        folder_path = os.path.join(self.questions_dir, folder)
        
        q_index = self.get_question_index()
        
        new_files = []
        for i, old_name in enumerate(self.current_images):
            ext = os.path.splitext(old_name)[1].lower()
            if not ext:
                ext = ".png"
            new_name = f"image-{q_index}_{i + 1}{ext}"
            new_path = os.path.join(folder_path, new_name)
            
            if old_name != new_name:
                os.rename(os.path.join(folder_path, old_name), new_path)
            
            new_files.append(new_name)
        
        self.current_images = new_files
        
        correct_alt = self.combo_correct.get()
        alternatives = []
        
        for letter in ["A", "B", "C", "D", "E"]:
            text = self.alt_entries[letter].get()
            is_correct = (letter == correct_alt)
            alternatives.append({
                "letter": letter,
                "text": text,
                "file": None,
                "isCorrect": is_correct
            })
        
        data = {
            "title": self.entry_title_q.get(),
            "index": int(self.entry_index.get()) if self.entry_index.get().isdigit() else 1,
            "year": int(self.entry_year_q.get()) if self.entry_year_q.get().isdigit() else 2024,
            "language": self.combo_language.get() or None,
            "discipline": self.combo_discipline.get(),
            "context": self.text_context.get("1.0", tk.END).strip(),
            "files": new_files,
            "correctAlternative": correct_alt,
            "alternativesIntroduction": self.text_alt_intro.get("1.0", tk.END).strip(),
            "alternatives": alternatives
        }
        
        with open(details_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        messagebox.showinfo("Saved", f"Saved to {details_path}")
        
        self.load_folder_images()
    
    def go_previous(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_current_question()
    
    def go_next(self):
        if self.current_index < len(self.folders) - 1:
            self.current_index += 1
            self.load_current_question()
    
    def on_jump_focus_out(self, event):
        val = self.entry_jump.get().strip()
        if val.isdigit():
            target = int(val) - 1
            total = len(self.folders)
            if target < 0:
                target = 0
            elif target >= total:
                target = total - 1
            self.current_index = target
            self.load_current_question()
        self.entry_jump.delete(0, tk.END)
        self.entry_jump.insert(0, self.current_index + 1)

def main():
    root = tk.Tk()
    app = QuestionEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()