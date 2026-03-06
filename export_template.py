import os
try:
    import sqladmin
    t_path = os.path.join(os.path.dirname(sqladmin.__file__), 'templates', 'sqladmin', 'layout.html')
    if os.path.exists(t_path):
        with open(t_path, 'r') as f:
            with open('/home/cluna/Documentos/5-IA/5-Freelance/4-Consultorio Odontologico/sqladmin_layout_backup.html', 'w') as out:
                out.write(f.read())
        print("Success")
    else:
        print("Template not found at: " + t_path)
except Exception as e:
    print(str(e))
