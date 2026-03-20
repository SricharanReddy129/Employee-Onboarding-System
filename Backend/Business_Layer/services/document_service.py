from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import os
from datetime import datetime

class DocumentService:

    def generate_offer_pdf(self, offer_data):

        # Load template
        env = Environment(loader=FileSystemLoader("Backend/templates"))
        template = env.get_template("offer_letter.html")

        # Render HTML
        # html_content = template.render(offer_data)
        html_content = template.render({
                **offer_data,
                "current_date": datetime.today().strftime("%d %B %Y")
            })

        # Ensure folder exists
        os.makedirs("generated_pdfs", exist_ok=True)

        output_path = f"generated_pdfs/offer_{offer_data['user_uuid']}.pdf"

        # Generate PDF
        HTML(string=html_content).write_pdf(output_path)

        return output_path