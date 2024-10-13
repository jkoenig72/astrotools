# astrotools

renameAstroPhoto.py: 
This script processes astrophotography images by extracting metadata from associated FITS files and renaming the images accordingly. It also generates an .info file with detailed observation data and overlays text onto the images with key information. The script uses the following command-line parameters:

--pathtofit: (Required) The path to the FITS file from which to extract metadata.
--picturepath: (Required) The path to the image file to be renamed and annotated.

watchdog.py:
This script functions as a watchdog for the indi-allsky software, which captures all-sky images for astronomical observations. It ensures the continuous operation of the indi-allsky service by monitoring the age of the latest image file generated. If the image is older than allowed thresholds, the script takes corrective actions such as restarting services or rebooting machines.

asiairFC.py:
This script automates the process of copying files from multiple ASIAIR devices to a local storage location. ASIAIR devices are used in astrophotography setups for controlling cameras and telescopes. The script connects to multiple ASIAIR devices over the network via SMB (Server Message Block) protocol, checks which devices are online, and copies their shared files to corresponding local directories, organizing them by date.
