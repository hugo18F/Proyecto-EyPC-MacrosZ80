import re
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk 

# Configuración de customtkinter
ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("blue")  

def expand_macros(input_code):
    """
    Expande macros definidas en el código de entrada y reemplaza sus llamadas por el contenido correspondiente.
    Lanza un error si hay problemas de definición de parámetros o etiquetas.
    """
    lines = [line.strip() for line in input_code.split('\n')]
    macros = {}
    expanded_code = []
    in_macro = False
    macro_name = ''
    macro_content = []
    macro_params = []
    defined_labels = set()

    # Primera pasada: identificar etiquetas y definiciones
    for line in lines:
        label_match = re.match(r'^(\w+):', line)
        if label_match:
            defined_labels.add(label_match.group(1))

    # Segunda pasada: procesar macros y validaciones
    for line in lines:
        if ': MACRO' in line:
            in_macro = True
            parts= line.split(':')
            macro_name = parts[0].strip()
            macro_params = [
                param.strip()
                for param in parts[1].replace('MACRO', '').strip().split(',')
            ]
            macro_content = []
            continue
        if line == 'ENDM':
            in_macro = False
            for macro_line in macro_content:
                for word in re.findall(r'\b\w+\b', macro_line):
                    if word not in macro_params and word not in defined_labels and not re.match(r'^[A-Z]+$', word):
                        raise ValueError(
                            f"Error en la macro '{macro_name}': "
                            f"El parámetro o etiqueta '{word}' no está definido."
                        )
            macros[macro_name] = {"content": macro_content, "params": macro_params}
            continue

        if in_macro:
            macro_content.append(line)
        else:
            expanded_code.append(line)

    final_code = []
    for line in expanded_code:
        macro_call_match = re.match(r'^(\w+)\s*(.*)$', line)
        if macro_call_match:
            call_name, args_string=macro_call_match.groups()
            if call_name in macros:
                args = [arg.strip() for arg in args_string.split(',')]
                macro_body = macros[call_name]["content"]
                macro_params = macros[call_name]["params"]

                if len(args) != len(macro_params):
                    raise ValueError(
                        f"Error: La macro '{call_name}' esperaba {len(macro_params)} argumentos, "
                        f"pero se proporcionaron {len(args)}."
                    )

                for macro_line in macro_body:
                    expanded_line = macro_line
                    for index, arg in enumerate(args):
                        macro_arg = macro_params[index]
                        expanded_line = re.sub(rf'\b{macro_arg}\b', arg, expanded_line)
                    final_code.append(expanded_line)
            else:
                final_code.append(line)
        else:
            final_code.append(line)

    return '\n'.join(final_code)

def handle_expand():
    """
    Expande el código de entrada y muestra el resultado en `output_text`.
    Muestra un error si falla la expansión.
    """
    try:
        input_code = input_text.get("1.0", tk.END).strip()
        expanded_code =expand_macros(input_code)
        output_text.delete("1.0",tk.END)
        output_text.insert("1.0", expanded_code)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def copy_to_clipboard():
    """
    Copia el código expandido al portapapeles y muestra un mensaje de éxito.
    Muestra una advertencia si no hay contenido para copiar.
    """
    expanded_code =output_text.get("1.0", tk.END).strip()
    if expanded_code:
        root.clipboard_clear()
        root.clipboard_append(expanded_code)
        root.update()
        messagebox.showinfo("Copiar", "Código expandido copiado al portapapeles.")
    else:
        messagebox.showwarning("Advertencia", "No hay código expandido para copiar.")

def save_to_file():
    """
    Guarda el contenido del widget `output_text` en un archivo de texto seleccionado.
    Muestra un mensaje de advertencia si no hay contenido para guardar.
    """
    expanded_code = output_text.get("1.0", tk.END).strip()
    if expanded_code:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            with open(file_path, "w") as file:
                file.write(expanded_code)
            messagebox.showinfo("Guardar", f"Código expandido guardado en: {file_path}")
    else:
        messagebox.showwarning("Advertencia", "No hay código expandido para guardar.")

def load_from_file():
    """
    Carga el contenido de un archivo de texto seleccionado en el widget`input_text`.
    Muestra un mensaje de error si la carga falla.
    """
    file_path = filedialog.askopenfilename(
        filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
    )
    if file_path:
        try:
            with open(file_path, "r") as file:
                content = file.read()
                input_text.delete("1.0", tk.END)
                input_text.insert("1.0", content)
                messagebox.showinfo("Cargar", f"Archivo cargado desde: {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo: {str(e)}")


# Configuración de tkinter
root = ctk.CTk()
root.title("MACROZ80")
root.geometry("900x1000")

dark_blue = "#4F91A6" 

title_label = ctk.CTkLabel(root, text="MACROZ80", font=("Montserrat", 30, "bold"))
title_label.pack(pady=20)

load_button = ctk.CTkButton(root, text="Importar Archivo", command=load_from_file, width=160, height=40,corner_radius=20, fg_color=dark_blue, text_color="black", font=("Montserrat", 16))
load_button.pack(anchor="w", padx=40, pady=10)

input_label = ctk.CTkLabel(root, text="Código con Macros:",font=("Montserrat", 18))
input_label.pack(anchor="w", padx=40)

input_text = ctk.CTkTextbox(root, height=300, font=("Consolas",16), corner_radius=15)
input_text.pack(fill="x", padx=40, pady=10)

expand_button = ctk.CTkButton(root,text="Expandir Macros", command=handle_expand, height=60, corner_radius=20, fg_color=dark_blue, text_color="black", font=("Montserrat", 16))
expand_button.pack(pady=10)

output_label = ctk.CTkLabel(root, text="Código Expandido:", font=("Montserrat", 18))
output_label.pack(anchor="w", padx=40)

output_text = ctk.CTkTextbox(root, height=300, font=("Consolas", 16), corner_radius=15)
output_text.pack(fill="x", padx=40, pady=10)

button_frame = ctk.CTkFrame(root)
button_frame.pack(fill="x", pady=10, padx=40)

copy_button = ctk.CTkButton(button_frame, text="Copiar al Portapapeles",command=copy_to_clipboard, corner_radius=20, fg_color=dark_blue, text_color="black", font=("Montserrat", 16))
copy_button.pack(side="left", expand=True, fill="x", padx=5)

save_button = ctk.CTkButton(button_frame, text="Guardar en Archivo", command=save_to_file, corner_radius=20, fg_color=dark_blue, text_color="black", font=("Montserrat", 16))
save_button.pack(side="left", expand=True, fill="x", padx=5)

# Iniciar la aplicación
root.mainloop()
