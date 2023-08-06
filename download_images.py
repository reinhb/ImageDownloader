import os
import requests
import sys

### CONFIG ###
root_save_directory = 'downloaded'

api_root_url = ''
api_user = ''
api_key = ''

# Number of pages to fetch
max_num_pages_to_fetch = 100

# Number of images on each page [1-100]
page_size = 100

# Image resolution
# 1 = Thumbnail 192px
# 2 = Small 420px
# 4 = Medium w/ watermark 1000px
# 8 = Medium w/o watermark 1000px
# 9 = High > 1000px
# Note: 8 and 9 requires extra permission.
image_res = 2
###

headers={'x-api-user': api_user, 'x-api-key': api_key, 'Content-Type': 'application/json'}

def download_and_save_image_to_file(image_data, save_directory):
    (pictureid, db) = image_data
    print(f"Fetching image with pictureid: {pictureid} from db: {db}...", end="")
    json_body = {'pictureid': pictureid, 'db': db, 'res': image_res}
    response = requests.get(f'{api_root_url}/download', headers=headers, json=json_body)

    if response.status_code == 200:
        # Get the file extension from the Content-Type header
        content_types = response.headers['Content-Type'].split(';')[0]
        file_extension = content_types.split('/')[-1]

        # Create the file path
        file_path = os.path.join(save_directory, f'{pictureid}.{file_extension}')
        
        print(f" saving image to '{file_path}...", end="")
        # Write the image data to file
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(" Done!")
        return True
    else:
        print(f' Failed. Status code: {response.status_code}.')
        return False


def fetch_image_data_for_download(querystring, start_position):
    all_image_data = []

    # Current page number
    page = 0
    
    while page < max_num_pages_to_fetch:
        offset_position = start_position + page * page_size
        print(f"Fetching ids from page: {page}, position: {offset_position}.")

        json_body = {'querystring': querystring, 'from': offset_position, 'size': page_size}
        response = requests.get(f'{api_root_url}/search', headers=headers, json=json_body)

        if response.status_code == 200:
            data = response.json()

            # Check the response if it contains pictures
            if(len(data) < 2 or data[0]["total"] == 0):
                print("Found no images matching query.")
                break

            # Extract the pictureid and db for each image
            pictures = data[1]['pictures']
            current_page_picture_data = [(item['pictureid'], item['db']) for item in pictures]

            # Add pictureid and db info to the list
            all_image_data.extend(current_page_picture_data)

            num_pictures_current_page = len(current_page_picture_data)
            
            # If the number of items in the response is less than the page size, this is the last page
            if num_pictures_current_page < page_size:
                print(f"Reached last page.")
                break

            # Go to the next page
            page += 1
        else:
            print(f'Failed to fetch metadata. Status code: {response.status_code}')
            break

    return all_image_data


def create_save_directory(querystring):
    folder_name = querystring.replace(" ", "_")
    save_directory = f"{root_save_directory}/{folder_name}"
    # Create the folder if it doesn't exist
    os.makedirs(save_directory, exist_ok=True)
    return save_directory


def download_and_save_all_images(all_image_data, save_directory):
    error_counter = 0
    print("Starting download of images...")
    for image_data in all_image_data:
        success = download_and_save_image_to_file(image_data, save_directory)
        if(not success):
           error_counter += 1
        elif(error_counter > 0):
            error_counter -= 1
        if(error_counter >= 10):
            print("Too many errors. Aborting script.")
            sys.exit()
           


def search_and_save_images(querystring, start_position=0):
    print(f"Current config: resolution={image_res}, page size={page_size}, number of pages to fetch={max_num_pages_to_fetch}.")
    print(f"Searching for images matching: '{querystring}, from start position: {start_position}.")
    all_image_data = fetch_image_data_for_download(querystring, start_position)
    print(f'Found {len(all_image_data)} images for querystring: {querystring}.')

    if(len(all_image_data) > 0):
        save_directory = create_save_directory(querystring)
        print(f"Saving images in directory: '{save_directory}'.")
        download_and_save_all_images(all_image_data, save_directory)


def main():
    num_args = len(sys.argv)
    if num_args == 3:
        search_and_save_images(sys.argv[1], int(sys.argv[2]))
    elif num_args == 2:
        search_and_save_images(sys.argv[1])
    else:
        print("You must provide a search query")


if __name__ == "__main__":
    main()