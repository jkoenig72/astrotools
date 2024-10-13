import argparse
import os
from astropy.io import fits
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import shutil  # Import shutil for copying files

def extract_fits_info(fits_file):
    """
    Extracts information from a FITS file.

    Parameters
    ----------
    fits_file : str
        The path to the FITS file from which to extract information.

    Returns
    -------
    tuple
        A tuple containing formatted date of observation, telescope name,
        instrument name, exposure time, focal length, CCD temperature,
        right ascension, declination, image width, image height, creator,
        guide camera, Bayer pattern, and gain.
    """
    with fits.open(fits_file) as hdul:
        header = hdul[0].header

        # Extract creator information from FITS header
        creator = header.get('CREATOR', 'Unknown')
        if creator == 'Unknown':
            creator = header.get('SWCREATE', 'Unknown')

        # Extract and parse CCD Temperature
        ccd_temp_value = header.get('CCD-TEMP', 'Unknown')
        try:
            ccd_temp = round(float(ccd_temp_value), 2)
        except (ValueError, TypeError):
            ccd_temp = 'Unknown'

        # Extract and parse Right Ascension
        ra_value = header.get('RA', 'Unknown')
        try:
            ra = round(float(ra_value), 2)
        except (ValueError, TypeError):
            ra = 'Unknown'

        # Extract and parse Declination
        dec_value = header.get('DEC', 'Unknown')
        try:
            dec = round(float(dec_value), 2)
        except (ValueError, TypeError):
            dec = 'Unknown'

        # Extract other details from FITS header
        date_obs = header.get('DATE-OBS', 'Unknown')
        telescope = header.get('TELESCOP', 'Unknown')
        instrument = header.get('INSTRUME', 'Unknown')
        guidecam = header.get('GUIDECAM', 'Unknown')
        bayerpat = header.get('BAYERPAT', 'Unknown')
        gain = header.get('GAIN', 'Unknown')

        # Extract and parse Exposure Time
        exposure_value = header.get('EXPOSURE', 'Unknown')
        try:
            exposure = float(exposure_value)
        except (ValueError, TypeError):
            exposure = 'Unknown'

        # Extract image dimensions
        imagew = header.get('IMAGEW', 'Unknown')
        if imagew == 'Unknown':
            imagew = header.get('NAXIS1', 'Unknown')

        imageh = header.get('IMAGEH', 'Unknown')
        if imageh == 'Unknown':
            imageh = header.get('NAXIS2', 'Unknown')

        # Extract and parse Focal Length
        focal_length_value = header.get('FOCALLEN', 'Unknown')
        try:
            focal_length = float(focal_length_value)
        except (ValueError, TypeError):
            focal_length = 'Unknown'

        # Format the observation date
        try:
            formatted_date_obs = datetime.strptime(date_obs, '%Y-%m-%dT%H:%M:%S.%f').strftime('%Y%m%d_%H%M%S')
        except (ValueError, TypeError):
            formatted_date_obs = date_obs

        return (
            formatted_date_obs,
            telescope,
            instrument,
            exposure,
            focal_length,
            ccd_temp,
            ra,
            dec,
            imagew,
            imageh,
            creator,
            guidecam,
            bayerpat,
            gain
        )

def rename_picture(fits_info, picture_path):
    """
    Renames a picture file based on FITS file information.

    Parameters
    ----------
    fits_info : tuple
        Information extracted from the FITS file.
    picture_path : str
        The path to the picture file to be renamed.

    Returns
    -------
    str
        The new file path of the renamed picture.
    """
    # Extract object name and file extension from picture filename
    object_name, file_extension = os.path.splitext(os.path.basename(picture_path))

    # Create new filename using FITS info
    new_filename = f"{fits_info[0]}_{object_name}_{fits_info[1]}_{fits_info[2]}_EX{str(fits_info[3]).replace('.', 'p')}_FL{fits_info[4]}{file_extension}"
    new_filename = new_filename.replace(' ', '')  # Remove any spaces for cleaner filenames
    new_filepath = os.path.join(os.path.dirname(picture_path), new_filename)

    # Rename the file
    os.rename(picture_path, new_filepath)
    print(f"File renamed to: {new_filepath}")
    return new_filepath

def create_info_file(fits_info, new_filepath, object_name):
    """
    Creates an info file containing FITS information.

    Parameters
    ----------
    fits_info : tuple
        Information extracted from the FITS file.
    new_filepath : str
        The path to the renamed picture file.
    object_name : str
        The name of the observed object.
    """
    info_filepath = os.path.splitext(new_filepath)[0] + '.info'
    with open(info_filepath, 'w') as file:
        file.write(f"Object Name: {object_name}\n")
        try:
            date_str = datetime.strptime(fits_info[0], '%Y%m%d_%H%M%S').strftime('%d.%m.%Y %H:%M:%S')
        except (ValueError, TypeError):
            date_str = fits_info[0]
        file.write(f"Date/Time of Observation: {date_str}\n")
        file.write(f"Mount: {fits_info[1]}\n")
        file.write(f"Main Camera: {fits_info[2]}\n")
        file.write(f"Guide Camera: {fits_info[11]}\n")
        file.write(f"Exposure Time: {fits_info[3]}\n")
        file.write(f"Focal Length: {fits_info[4]}\n")
        file.write(f"CCD Temperature: {fits_info[5]}\n")
        file.write(f"Right Ascension: {fits_info[6]}\n")
        file.write(f"Declination: {fits_info[7]}\n")
        file.write(f"Image Width: {fits_info[8]}\n")
        file.write(f"Image Height: {fits_info[9]}\n")
        file.write(f"Creator: {fits_info[10]}\n")
        file.write(f"Bayer Pattern: {fits_info[12]}\n")
        file.write(f"Gain: {fits_info[13]}\n")
    print(f"Info file created at: {info_filepath}")

def add_text_to_picture(image_path, fits_info, object_name):
    """
    Adds text information onto a picture file.

    Parameters
    ----------
    image_path : str
        The path to the image file where text will be added.
    fits_info : tuple
        Information extracted from the FITS file.
    object_name : str
        The name of the observed object.
    """
    # Open the picture using Pillow
    image = Image.open(image_path)

    # Make a copy of the image
    image_copy = image.copy()

    # Create a Draw object to add text
    draw = ImageDraw.Draw(image_copy)

    # Set font, position, and color for the text
    font = ImageFont.truetype('/usr/share/fonts/truetype/freefonts/FreeSans.ttf', 12)
    text_color = (255, 255, 255)  # White
    text_position = (image_copy.width - 300, image_copy.height - 200)

    # Compile text from FITS info
    try:
        date_str = datetime.strptime(fits_info[0], '%Y%m%d_%H%M%S').strftime('%d.%m.%Y %H:%M:%S')
    except (ValueError, TypeError):
        date_str = fits_info[0]

    text = f"Object: {object_name}\n"
    text += f"Date/Time of Observation: {date_str}\n"
    text += f"Mount: {fits_info[1]}\n"
    text += f"Main Camera: {fits_info[2]}\n"
    text += f"Guide Camera: {fits_info[11]}\n"
    text += f"Exposure Time: {fits_info[3]}\n"
    text += f"Focal Length: {fits_info[4]}\n"
    text += f"CCD Temperature: {fits_info[5]}\n"
    text += f"Right Ascension: {fits_info[6]}\n"
    text += f"Declination: {fits_info[7]}\n"
    text += f"Image Width: {fits_info[8]}\n"
    text += f"Image Height: {fits_info[9]}\n"
    text += f"Creator: {fits_info[10]}\n"
    text += f"Gain: {fits_info[13]}\n"

    draw.text(text_position, text, fill=text_color, font=font)

    # Save the copied image with added text
    new_image_path = os.path.splitext(image_path)[0] + '_with_text' + os.path.splitext(image_path)[1]
    image_copy.save(new_image_path)

    print(f"Info added to the picture. Picture saved at: {new_image_path}")

def main():
    """
    Main function to handle argument parsing and execute the FITS extraction
    and processing pipeline including renaming picture files, creating info
    files, and adding text overlay to pictures.
    """
    parser = argparse.ArgumentParser(description="Extract information from a FITS file and rename a picture file.")
    parser.add_argument("--pathtofit", help="Path to the FITS file")
    parser.add_argument("--picturepath", help="Path to the picture file")
    args = parser.parse_args()

    fits_file = args.pathtofit
    picture_path = args.picturepath

    object_name = os.path.splitext(os.path.basename(picture_path))[0]

    # Extract information from FITS file
    fits_info = extract_fits_info(fits_file)

    # Convert fits_info to a list to allow modifications
    fits_info = list(fits_info)

    # Prompt the user for the guide camera if it's unknown
    if fits_info[11] == 'Unknown':
        guidecam_input = input("Guide Camera not found in FITS header. Please enter Guide Camera: ")
        fits_info[11] = guidecam_input

    fits_info = tuple(fits_info)  # Convert back to tuple if necessary

    # Rename the picture file
    new_filepath = rename_picture(fits_info, picture_path)

    # Create the info file
    create_info_file(fits_info, new_filepath, object_name)

    # Add text to the picture
    add_text_to_picture(new_filepath, fits_info, object_name)

if __name__ == "__main__":
    main()