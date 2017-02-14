#!/bin/bash
#this script will change the thumbnails of all vcards to images (of the same name) generated by a seperate python script.   

#this directory points to vcards you want to thumbnail
VCARDS=/home/Contacts/*.vcf

#this directory points to the directory where thumbnails will be stored
THUMBNAIL_DIR=/.vcardthumnails/

for card in $VCARDS
do
	#checks to see if generated icon exists, if no, generate thumbnail. if yes, assign thumbnail. 
	if [ ! -f "$THUMBNAIL_DIR/$card.png" ]; then
		#python generatethumbnail.py $f
	else	
		gvfs-set-attribute -t string $card metadata::custom-icon file:///.vcardthumbnails/"$card.png"
	fi

	#this script might also increase the size of vcard thumbnails.
done
