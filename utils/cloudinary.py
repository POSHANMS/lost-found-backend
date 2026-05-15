import cloudinary
import cloudinary.uploader
import os

# configure cloudinary with credentials from .env
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

def upload_image(file, folder="findit"):
    """
    Uploads an image file to Cloudinary.
    Returns the secure HTTPS URL of the uploaded image.
    """
    result = cloudinary.uploader.upload(file, folder=folder)    # store in findit folder on cloudinary
    return result["secure_url"]                 # get the HTTPS URL back

def delete_image(public_id):
    """
    Deletes an image from Cloudinary by its public_id.
    Called when an item is deleted.
    """
    cloudinary.uploader.destroy(public_id)