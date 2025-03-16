import os

# Générer HTML avec Redoc
os.system("redoc-cli bundle static/openapi.yaml -o docs/API_Documentation.html")

# Convertir HTML en PDF
os.system("wkhtmltopdf docs/API_Documentation.html docs/API_Documentation.pdf")

print("📄 Documentation PDF générée avec succès : docs/API_Documentation.pdf")
