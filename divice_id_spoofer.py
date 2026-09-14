import customtkinter as ctk
import random
import pymem
import pymem.pattern
import threading

patterns = [
    (b'","atyp":"', - 32),
    (b'"ClientId":"', + 12)

]

VERSION = "1.0.5"

class GUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.did = ""
        self.current_did = ""
        self.found = False
        self.pm = None
        self.inject()
        self.build_gui()
    def build_gui(self):
        self.title("Divice ID Spoofer")
        self.geometry("430x200")

        self.label = ctk.CTkLabel(self, text="Device ID Spoofer by Blockhunter", font=("Arial", 16))
        self.label.pack(pady=(30, 10))

        self.controls = ctk.CTkFrame(self, fg_color="transparent")
        self.controls.place(relx=0.5, rely=0.5, anchor="center")

        self.did_entry = ctk.CTkEntry(self.controls, placeholder_text="Enter DID", width=180)
        self.did_entry.grid(row=0, column=0, padx=5)
        self.did_entry.insert(0, self.did)

        self.did_randomize_button = ctk.CTkButton(self.controls, text="Randomize", width=60, command=self.randomize_did)
        self.did_randomize_button.grid(row=0, column=1, padx=5)

        self.did_apply_button = ctk.CTkButton(self.controls, text="Apply", width=60, command=self.apply_did)
        self.did_apply_button.grid(row=0, column=3, padx=5)

        self.did_reset_button = ctk.CTkButton(self.controls, text="Reset", width=80, command=self.reset_did)
        self.did_reset_button.grid(row=0, column=2, padx=5)

        self.version_label = ctk.CTkLabel(self, text=f"Version: {VERSION}", font=("Arial", 12))
        self.version_label.place(relx=0.5, rely=0.9, anchor="center")

        self.game_not_found_label = ctk.CTkLabel(self, text="Game not found!", font=("Arial", 12), text_color="red")

        if not self.found:
            self.controls.pack_forget()
            self.game_not_found_label.place(relx=0.5, rely=0.5, anchor="center")
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    def inject(self):
        try:
            self.pm = pymem.Pymem("Minecraft.Windows.exe")
            for pattern, offset in patterns:
                result = pymem.pattern.pattern_scan_all(self.pm.process_handle, pattern)
                if result:
                    result += offset
                    break
            else:
                raise Exception("Pattern not found")
            self.did = self.pm.read_bytes(result, 32).decode("ascii")
            print(f"[BLS] Found DID: {self.did}")
            self.current_did = self.did
            self.found = True
        except Exception as e:
            print(f"[BLS] Error occurred while injecting: {e}")
            self.found = False
    def randomize_did(self):
        threading.Thread(target=self._randomize_did).start()
    def _ui_call(self, func, *args, **kwargs):
        self.after(0, lambda: func(*args, **kwargs))
    def _randomize_did(self):
        self._disable_controls()
        if self.found:
            new_did = self.did_entry.get()
            if False:
                if not new_did or len(new_did) != 32:
                    new_did = new_did + ''.join(random.choices('0123456789abcdef', k=(32 - len(new_did))))
            else:
                new_did = ''.join(random.choices('0123456789abcdef', k=32))
            self._ui_call(self.did_entry.configure, state="normal")
            self._ui_call(self.did_entry.delete, 0, 'end')
            self._ui_call(self.did_entry.insert, 0, new_did)
        self._enable_controls()
    def reset_did(self):
        threading.Thread(target=self._reset_did).start()
    def _reset_did(self):
        self._ui_call(self.did_reset_button.configure, text="Resetting...")
        self._disable_controls()
        if self.found:
            self._write_did(self.did)
            self._ui_call(self.did_entry.configure, state="normal")
            self._ui_call(self.did_entry.delete, 0, 'end')
            self._ui_call(self.did_entry.insert, 0, self.did)
        self._enable_controls()
        self._ui_call(self.did_reset_button.configure, text="Reset")
    def apply_did(self):
        threading.Thread(target=self._apply_did).start()
    def _apply_did(self):
        self._ui_call(self.did_apply_button.configure, text="Applying...")
        self._disable_controls()
        if self.found:
            new_did = self.did_entry.get()
            if not new_did or len(new_did) != 32:
                new_did = new_did + ''.join(random.choices('0123456789abcdef', k=(32 - len(new_did))))
            self._write_did(new_did)
            self.current_did = new_did
        self._enable_controls()
        self._ui_call(self.did_apply_button.configure, text="Apply")
    def _disable_controls(self):
        self._ui_call(self.did_entry.configure, state="disabled")
        self._ui_call(self.did_randomize_button.configure, state="disabled")
        self._ui_call(self.did_apply_button.configure, state="disabled")
        self._ui_call(self.did_reset_button.configure, state="disabled")
    def _enable_controls(self):
        self._ui_call(self.did_entry.configure, state="normal")
        self._ui_call(self.did_randomize_button.configure, state="normal")
        self._ui_call(self.did_apply_button.configure, state="normal")
        self._ui_call(self.did_reset_button.configure, state="normal")
    def _write_did(self, new_did):
        if self.found:
            if len(new_did) > 32:
                new_did = new_did[:32]
            resuts = pymem.pattern.pattern_scan_all(self.pm.process_handle, bytes(self.current_did, 'ascii'), return_multiple=True)
            for result in resuts:
                try:
                    self.pm.write_bytes(result, bytes(new_did, 'ascii'), len(new_did))
                except Exception as e:
                    print(f"[BLS] Error occurred while resetting DID: {e}")
            self.current_did = new_did
    def _on_close(self):
        self.destroy()
        self._write_did(self.did)

if __name__ == "__main__":
    app = GUI()
    app.mainloop()
