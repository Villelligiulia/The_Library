import requests
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from books.models import Book, Author, Category
import pandas as pd


class Command(BaseCommand):
    help = 'Import books from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        file_path = options['file_path']

        # Load CSV file using pandas
        df = pd.read_csv(file_path)

        # Iterate over each row in the DataFrame
        for _, row in df.iterrows():
            title = row['Title']
            author_name = row['Authors']
            category_name = row['Category']
            price = row['Price']
            description = row['Book_Description']
            image_url = row['Image_Link']
            ratings = row['Ratings']

            # Download the image from the URL
            response = requests.get(image_url)
            if response.status_code == 200:
                # Save the image locally
                image_name = image_url.split('/')[-1]
                image_path = f'book_covers/{image_name}'
                image_content = ContentFile(response.content)
                default_storage.save(image_path, image_content)

                # Get or create the author
                author, _ = Author.objects.get_or_create(name=author_name)

                # Get or create the category
                category, _ = Category.objects.get_or_create(
                    name=category_name)

                # Create the book associated with the author
                book = Book.objects.create(
                    title=title,
                    author=author,
                    category=category,
                    price=price,
                    description=description,
                    cover_image=image_path,
                    ratings=ratings,
                )

                # Display success message
                self.stdout.write(self.style.SUCCESS(
                    f'Successfully imported book: {book}'))
            else:
                # Display error message
                self.stderr.write(self.style.ERROR(
                    f'Failed to download image for book: {title}'))

        self.stdout.write(self.style.SUCCESS('Book import completed'))
