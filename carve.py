import pytsk3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import os

class JPEGRecoveryApp:
    def __init__(self, master):
        self.master = master
        master.title("JPEG Recovery Tool")
        master.configure(bg="#ADD8E6")  # Light blue background

        # --- Directory Selection ---
        self.dir_label = tk.Label(master, text="Enter Directory Path or Browse:", bg="#ADD8E6", fg="navy")
        self.dir_label.pack(pady=5)

        self.dir_entry = tk.Entry(master, width=40)
        self.dir_entry.pack(pady=5)

        self.browse_button = tk.Button(master, text="Browse", command=self.browse_directory, bg="lightblue", fg="black")
        self.browse_button.pack(pady=2)

        # --- Drive Selection (Optional - You can keep this if you want both options) ---
        self.drive_label = tk.Label(master, text="Or Enter Drive Path (e.g., \\\\.\\D:):", bg="#ADD8E6", fg="navy")
        self.drive_label.pack(pady=5)

        self.drive_entry = tk.Entry(master, width=30)
        self.drive_entry.pack(pady=5)

        # --- Scan Button ---
        self.scan_button = tk.Button(master, text="Scan for JPEG", command=self.scan_for_jpeg, bg="blue", fg="white", width=20)
        self.scan_button.pack(pady=10)

        # --- Progress Bar ---
        self.progress = ttk.Progressbar(master, orient="horizontal", length=300, mode="indeterminate")
        self.progress.pack(pady=10)

        # --- Status Label ---
        self.status_label = tk.Label(master, text="", bg="#ADD8E6", fg="navy")
        self.status_label.pack(pady=5)

        # --- Image Display ---
        self.image_frame = tk.Frame(master, bg="#ADD8E6")
        self.image_frame.pack(pady=10)

        self.image_label = tk.Label(self.image_frame, bg="#ADD8E6")
        self.image_label.pack(side=tk.LEFT)

        # --- File Name Label ---
        self.filename_label = tk.Label(master, text="", bg="#ADD8E6", fg="darkgreen")
        self.filename_label.pack()

    def browse_directory(self):
        directory = filedialog.askdirectory()
        self.dir_entry.delete(0, tk.END)
        self.dir_entry.insert(0, directory)

    def scan_for_jpeg(self):
        # Prioritize directory entry, then drive entry
        directory = self.dir_entry.get()
        drive = self.drive_entry.get()

        if directory:
            self.recover_from_directory(directory)
        elif drive:
            self.status_label.config(text="Scanning drive...")
            self.progress.start(10)
            self.master.update_idletasks()
            try:
                img = pytsk3.Img_Info(drive)
                self.recover_latest_jpeg(img)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to access the drive: {e}")
                self.progress.stop()
                self.status_label.config(text="Scan Failed")
        else:
            messagebox.showerror("Error", "Please enter a directory or drive path.")

    def recover_from_directory(self, directory):
      
        self.status_label.config(text=f"Scanning directory: {directory}")
        self.progress.start(10)
        self.master.update_idletasks()
        
        try:
          for root, _, files in os.walk(directory):
            for file_name in files:
                if file_name.lower().endswith((".jpg", ".jpeg")):
                    file_path = os.path.join(root, file_name)
                    
                    try:
                        with open(file_path, "rb") as file:
                            
                            # Read the entire file content
                            file_data = file.read()
                            
                            # Basic JPEG header check
                            if file_data.startswith(b'\xff\xd8\xff'):
                                # Display the image
                                self.display_image(file_path, file_data)

                                self.status_label.config(text=f"Found: {file_name}")
                                self.filename_label.config(text=f"File: {file_name}")
                                self.master.update_idletasks()
                                return  # Stop after finding the first JPEG (optional)

                    except Exception as e:
                        messagebox.showerror("Error", f"Error processing {file_name}: {e}")
                        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to access directory: {e}")

        self.progress.stop()
        self.status_label.config(text="Directory Scan Complete")
        self.filename_label.config(text="") # Clear file name if no image found


    def recover_latest_jpeg(self, image_info):
        block_size = 512
        latest_image_data = bytearray()
        offset = 0
        recovered = False
        file_name = ""

        while True:
            try:
                data = image_info.read(offset, block_size)
            except IOError:
                break

            if not data:
                break

            start = data.find(b'\xff\xd8\xff\xe0')
            if start != -1:
                self.status_label.config(text=f"Found JPEG at offset: {hex(offset + start)}")
                latest_image_data = bytearray(data[start:])

                while True:
                    try:
                        offset += block_size
                        data = image_info.read(offset, block_size)
                    except IOError:
                        break

                    if not data:
                        break

                    end = data.find(b'\xff\xd9')
                    if end != -1:
                        latest_image_data.extend(data[:end + 2])
                        self.status_label.config(text="JPEG Recovery Complete")
                        recovered = True
                        break
                    else:
                        latest_image_data.extend(data)

                if recovered:
                    break

            offset += block_size
            self.master.update_idletasks()

        self.progress.stop()

        if latest_image_data:
            try:
                # Save and display the image
                temp_filename = "latest_recovered.jpg"
                with open(temp_filename, "wb") as file:
                    file.write(latest_image_data)

                self.display_image(temp_filename, latest_image_data)
                self.filename_label.config(text=f"File: {temp_filename}")
                messagebox.showinfo("Success", "Latest image recovered and displayed.")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to display the image: {e}")
        else:
            messagebox.showinfo("Info", "No JPEG images found.")
            self.filename_label.config(text="")  # Clear file name if no image found

    def display_image(self, file_path, image_data):
        try:
            img = Image.open(file_path)

            # Resize for display
            max_width = 400
            max_height = 300
            if img.width > max_width or img.height > max_height:
                ratio = min(max_width / img.width, max_height / img.height)
                new_width = int(img.width * ratio)
                new_height = int(img.height * ratio)
                img = img.resize((new_width, new_height))

            photo = ImageTk.PhotoImage(img)
            self.image_label.config(image=photo)
            self.image_label.image = photo  # Keep a reference
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display image: {e}")

root = tk.Tk()
app = JPEGRecoveryApp(root)
root.mainloop()