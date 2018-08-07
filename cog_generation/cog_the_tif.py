def get_command_line_arguments():
    #If the required command line arguments are not specified then
    #remind the user the require arguments and their format
    if(len(sys.argv) < 4):
        print()
        print("This program needs exactly 3 command line arguments!\n")
        print("The format for the arguments are:")
        print("1. Source Bucket Name (example: dev-lssa-c1-packaged)")
        print("2. Destination Bucket (example: dev-lsaa-c1-cog")
        print("3. Name of tar file (example: LC08_L1TP_044034_20150116_20170302_01_T1.tar.gz")
        print()
        exit()

    #Get the source and destination bucket names from command line arguments
    sourceName = sys.argv[1]
    destName = sys.argv[2]
    keyName = sys.argv[3]

    #Tell the user the buckets and the file that is being processed
    print("Source Bucket:  " + sourceName)
    print("Destination Bucket:  " + destName)
    print("File Key:  " + keyName)

    return sourceName, destName, keyName

def ODL_to_JSON_converter(path_of_odl):
    #Get the odl contents from the file
    with open(path_of_odl, "r") as odl_file:
        odl_contents = odl_file.read()
    
    odl_contents = odl_contents.replace(' (', '[').replace(')', ']')
    
    #ODL lists have 5 values per line, we want them on the same line.  This loop goes through the conents
    #character by character and identifies where the ODL lists are and brings them onto the same line.
    list_to_pop = []
    in_list = False
    for x in range(len(odl_contents)):
        if not in_list and odl_contents[x] == '[':
            in_list = True
        #If we encounter a space, tab, or newline in a list, we will add it to the list to pop
        elif in_list and (odl_contents[x] == '\n' or odl_contents[x] == '\t' or odl_contents[x] == ' '):
            list_to_pop.insert(0, x)
        elif in_list and odl_contents[x] == ']':
            in_list = False
    #Now we pop all the "bad" characters in the reverse order we found them to prevent out of range indexes  
    for x in list_to_pop:
        odl_contents = odl_contents[0:x] +  odl_contents[x+1:]
        
    #All the attribute-value pairs are now on the same line, so lets make a list that holds the pairs
    odl_lines = odl_contents.split('\n')

    #Create a list that holds a list of all the attribute-value pairs, first element in the pair list will be
    #the attribute, the second will be the actual value of the attribute
    odl_pair_list = []
    list_to_pop = []
    
    for line in odl_lines:
        odl_pair_list.append(line.replace("'", "").replace('"', '').replace('\n', '').split('='))
    for i, pair in enumerate(odl_pair_list):
        #If there is a line that is not a attribute-value pair, then get rid of it.
        #This could be comments, empty lines, or the END line of the file
        if(len(pair) != 2):
            list_to_pop.insert(0,i)
        else:
            odl_pair_list[i][0] = odl_pair_list[i][0].strip()
            odl_pair_list[i][1] = odl_pair_list[i][1].strip()
            
    #Pop the non-attribute-value pairs off the list
    for i in list_to_pop:
        odl_pair_list.pop(i)
        
    #Finally, lets convert the ODL format to a dictionary
    dictionary_of_metadata = odl_to_dictionary(odl_pair_list)
    
    return dictionary_of_metadata
    
        
#Function that actually converts the ODL to JSON. Uses recursion to nest the groups in the ODL.
def odl_to_dictionary(list_of_values):
    map_of_metadata = {}
    in_group = False
    
    for x in range(len(list_of_values)):
        if not in_group and list_of_values[x][0] == "GROUP":
            start_of_group = x
            in_group = True
        elif in_group and list_of_values[x][0] == "END_GROUP" and list_of_values[x][1] == list_of_values[start_of_group][1]:
            map_of_metadata[list_of_values[x][1]] = odl_to_dictionary(list_of_values[start_of_group+1:x])
            in_group = False
        elif not in_group:
            if list_of_values[x][1][0] == "[":
                map_of_metadata[list_of_values[x][0]] = ast.literal_eval(list_of_values[x][1])
            else:
                map_of_metadata[list_of_values[x][0]] = list_of_values[x][1]
                    
    return map_of_metadata


def download_object_from_s3(source_bucket_name, key_name, tar_file_name):
    #Record start time of the download
    dl_start_time = time.time()

    #Download the object from S3
    with open(tar_file_name, "wb") as tar_file:
        s3.download_fileobj(source_bucket_name, key_name, tar_file)

    #Record the total download time and inform the user
    total_DL_time = time.time() - dl_start_time
    print("Total Download Time: ", total_DL_time)


def extract_tar_file(tar_file_name, extract_file_path):
    #Record the start time for the untar process
    untar_start_time = time.time()

    #Try to untar all the contents from the file
    try:
        tar = tarfile.open(tar_file_name)
        tar.extractall(path=extract_file_path)
        tar.close()
        os.remove(tar_file_name)
    
    #If the untar process is unsucessful, exit the program
    except:
        print("Failed to extract the tar.gz file")
        exit()

    #Record the total time of the untar process and inform the user
    total_untar_time = time.time() - untar_start_time
    print("Total Untar Time: ", total_untar_time)


def get_tif_file_names(path_name):
    #Create list of TIF files that were inside the tar.gz
    tif_files = []

    for files in os.listdir(path_name):
        if files.endswith(".tif"):
            new_file = files.replace(".tif", ".TIF")
            rename_file(path_name + files, path_name + new_file)

    for files in os.listdir(path_name):
        if files.endswith(".TIF"):
            tif_files.append(path_name + files)

    return tif_files


def get_all_file_names(path_name, new_key):

    #Create list of all the files that were inside the tar.gz
    all_files = []

    for files in os.listdir(path_name):
        file_key = new_key + files
        all_files.append([path_name, files, file_key])

    return all_files


def cog_a_tif(tif_file_name):
    #Take the TIF file and use gdal to COG it
    if(tif_file_name.endswith(".tif")):
        tif_file_name_without_extension = tif_file_name.replace('.tif', '')

    elif(tif_file_name.endswith(".TIF")):
        tif_file_name_without_extension = tif_file_name.replace('.TIF', '')

    command = "mv {with_ext} {without}.TIF; /usr/local/bin/gdaladdo --config PREDICTOR_OVERVIEW 2 --config GDAL_TIFF_OVR_BLOCKSIZE 512 -q -ro -r average {without}.TIF 2 4 8 16 32; /usr/local/bin/gdal_translate -q {without}.TIF.ovr {without}_c.TIF.ovr -co TILED=YES -co COMPRESS=DEFLATE; mv {without}_c.TIF.ovr {without}.TIF.ovr; /usr/local/bin/gdal_translate {without}.TIF {without}_tiled_cloud.TIF -co TILED=YES -co COMPRESS=DEFLATE -co COPY_SRC_OVERVIEWS=YES -co BLOCKXSIZE=512 -co BLOCKYSIZE=512 --config GDAL_TIFF_OVR_BLOCKSIZE 512"
    command = command.format(with_ext = tif_file_name, without = tif_file_name_without_extension)
    os.system(command)

    #Delete files that we don't need anymore
    delete_file("{}.TIF".format(tif_file_name))
    delete_file("{}_tiled.TIF".format(tif_file_name))
    delete_file("{}_tiled.IMD".format(tif_file_name))
    delete_file("{}_c.TIF.IMD".format(tif_file_name))

    #Rename the files to fit the cloud storing format
    rename_file("{}_tiled.TIF.ovr".format(tif_file_name),"{}.ovr".format(tif_file_name))
    rename_file("{}_tiled_cloud.TIF".format(tif_file_name),"{}.TIF".format(tif_file_name))
    rename_file("{}_tiled_cloud.IMD".format(tif_file_name),"{}.IMD".format(tif_file_name))


def delete_file(file_name):
    try:
        os.remove(file_name)
    except OSError as e:
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occurred


def rename_file(file_name, new_name):
    try:
        os.rename(file_name, new_name)
    except OSError as e:
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occurred


def upload_and_delete(product_file_path, file_name, key_name, destination_bucket_name, product_dictionary):

    scene_md5, scene_sha, scene_md5_encode = sha_the_file.sha_and_md5(product_file_path + file_name)

    body_of_file = open(product_file_path + file_name, 'rb')

    s3.put_object(
        Body = body_of_file,
        Bucket = destination_bucket_name,
        Key = key_name,
        ContentMD5 = scene_md5_encode,
        Metadata = {
            'md5_Checksum': scene_md5,
            'sha512_Checksum': scene_sha,
            'product_id': product_dictionary["product_id"]
        }
    )

    delete_file(file_name[0]+file_name[1])

def start_state_machine_execution(all_files):
    metadata_txt_files = []
    metadata_xml_files = []
    cog_files = []

    for files in all_files:
        if files.endswith(".txt"):
            metadata_txt_files.append(files)
        elif files.endswith(".xml"):
            metadata_xml_files.append(files)
        else:
            cog_files.append(files)


def seperate_files(all_files):
    odl_files = []
    xml_files = []
    other_files = []

    for files in all_files:
        if files.lower().endswith(".xml"):
            xml_files.append(files)
        elif (files.lower().endswith(".txt") and (not files.endswith("GCP.txt"))):
            odl_files.append(files)
        else:
            other_files.append(files)

    return xml_files, odl_files, other_files

def XML_to_JSON_converter(path_of_xml):
    #Get the xml contents from the file
    with open(path_of_xml, "r") as xml_file:
        xml_contents = xml_file.read()

    #Use the xmltodict python library to turn the xml string to a python dictionary
    dictionary_of_metadata = xmltodict.parse(xml_contents)
    
    return dictionary_of_metadata


def xml_to_dictionary_converter(xml_files, file_path):
    json_dictionaries = []

    if xml_files:
        for xml_filename in xml_files:
            json_dictionaries.append([XML_to_JSON_converter(file_path + xml_filename), xml_filename.replace(".xml", ".json")])

    return json_dictionaries

def odl_to_dictionary_converter(odl_files, file_path):
    json_dictionaries = []

    if odl_files:
        for odl_filename in odl_files:
            json_dictionaries.append([ODL_to_JSON_converter(file_path + odl_filename), odl_filename.replace(".txt", ".json")])

    return json_dictionaries

def parse_metadata(json_dictionaries):
    scene_metadata = {}
    
    for json_dictionary in json_dictionaries:
        scene_metadata[json_dictionary[1]] = {
            "Type" : get_type_of_metadata(json_dictionary[0])
        }
        scene_metadata[json_dictionary[1]]["product_id"] = get_product_id(json_dictionary[0], scene_metadata[json_dictionary[1]]["Type"])
        scene_metadata[json_dictionary[1]]["product_metadata"] = decode_product_id(scene_metadata[json_dictionary[1]]["product_id"])
    
    primary_path, old_product_id, new_product_id = get_primary_product_id(json_dictionaries, scene_metadata)
    
    return scene_metadata, primary_path, old_product_id, new_product_id

def get_primary_product_id(json_dictionaries, scene_metadata):
    level_1_metadata = None
    level_2_metadata = None
    
    for json_dictionary in json_dictionaries:
        if scene_metadata[json_dictionary[1]]["Type"] == "Level_2_XML":
            level_2_metadata = json_dictionary[1]
        elif scene_metadata[json_dictionary[1]]["Type"] == "Level_1_MTL":
            level_1_metadata = json_dictionary[1]
            
    if(level_2_metadata):
        return level_2_metadata, scene_metadata[level_1_metadata]["product_id"], scene_metadata[level_2_metadata]["product_id"]
    elif(level_1_metadata):
        return level_1_metadata, None, scene_metadata[level_1_metadata]["product_id"]


def get_type_of_metadata(json_dictionary):
    if "espa_metadata" in json_dictionary:
        return "Level_2_XML"
    elif "L1_METADATA_FILE" in json_dictionary:
        return "Level_1_MTL"
    elif "EPHEMERIS" in json_dictionary:
        return "Level_1_ANG"
    else:
        return "Unknown"


def get_product_id(json_dictionary, metadata_type):
    if metadata_type == "Unknown":
        return "Unknown"
    
    elif metadata_type == "Level_1_ANG":
        return None
    
    elif metadata_type == "Level_1_MTL":
        try:
            return json_dictionary["L1_METADATA_FILE"]["METADATA_FILE_INFO"]["LANDSAT_PRODUCT_ID"]
        except KeyError:
            print("Error: Could not find Product_ID in Level 1 MTL")
            return "Unknown"
        
    elif metadata_type == "Level_2_XML":
        try:
            temp_product_id = json_dictionary["espa_metadata"]["global_metadata"]["product_id"]
            new_product_id = fix_product_id(json_dictionary, temp_product_id)
            change_level_2_metadata(json_dictionary, temp_product_id, new_product_id)
            return new_product_id
        except KeyError:
            print("Error: Could not find Product_ID in Level 2 XML")
            return "Unknown"


def decode_product_id(product_ID):
    if product_ID == "Unknown" or product_ID == None:
        return product_ID
    
    #Create a dictionary to hold the metadata of the scene
    scene_dict = {}
    scene_dict["product_id"] = product_ID
    scene_dict["sensor"] = product_ID[1]
    scene_dict["satellite"] = product_ID[0] + product_ID[2:4]
    scene_dict["correction_level"] = product_ID[5:9]
    scene_dict["WRS_path"] = product_ID[10:13]
    scene_dict["WRS_row"] = product_ID[13:16]
    scene_dict["acquisition_date"] = product_ID[17:25]
    scene_dict["acquisition_year"] = product_ID[17:21]
    scene_dict["process_date"] = product_ID[26:34]
    scene_dict["collection_number"] = product_ID[35:37]
    scene_dict["collection_category"] = product_ID[38:]

    #Change the dates from YYYYMMDD to YYYY-MM-DD format
    scene_dict["acquisition_date"] = scene_dict["acquisition_date"][0:4] + '-' + scene_dict["acquisition_date"][4:6] + '-' + scene_dict["acquisition_date"][6:8]
    scene_dict["process_date"] = scene_dict["process_date"][0:4] + '-' + scene_dict["process_date"][4:6] + '-' + scene_dict["process_date"][6:8]

    return scene_dict


def fix_product_id(json_dictionary, product_id):
    latest_production_date = get_latest_production_date(json_dictionary)
    latest_production_date = convert_date_to_product_standard(latest_production_date)
    
    product_id = product_id.replace("L1TP", "L2SP")
    product_id = product_id[0:26] + latest_production_date + product_id[34:]
    
    return product_id


def get_latest_production_date(json_dictionary):
        dates_of_bands = []
        for band in json_dictionary["espa_metadata"]["bands"]["band"]:
            timestamp = band["production_date"]
            try:
                ts = time.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
            except:
                ts = time.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
            string_of_date = time.strftime("%m/%d/%Y", ts)
            dates_of_bands.append(string_of_date)
            
        index_of_largest = 0
        for x in range(1, len(dates_of_bands)):
            if dates_of_bands[x] > dates_of_bands[index_of_largest]:
                index_of_largest = x
                
        return dates_of_bands[index_of_largest]


def convert_date_to_product_standard(latest_production_date):
    return latest_production_date[6:10] + latest_production_date[3:5] + latest_production_date[0:2]


def change_level_2_metadata(json_dictionary, old_product_id, new_product_id):
    try:
        json_dictionary["espa_metadata"]["global_metadata"]["product_id"] = json_dictionary["espa_metadata"]["global_metadata"]["product_id"].replace(old_product_id, new_product_id)

        for n, i in enumerate(json_dictionary["espa_metadata"]["bands"]["band"]):
            json_dictionary["espa_metadata"]["bands"]["band"][n]["file_name"] = json_dictionary["espa_metadata"]["bands"]["band"][n]["file_name"].replace(old_product_id, new_product_id)
            
    except:
        print("Unable to change Level 2 metadata to new Product ID")


def save_the_metadata(json_dictionaries, old_product_id, new_product_id, file_path):
    for json_dictionary in json_dictionaries:
        if(old_product_id):
            metadata_file_path = file_path + json_dictionary[1].replace(old_product_id, new_product_id)
        else:
            metadata_file_path = file_path + json_dictionary[1]
        with open(metadata_file_path, "w") as json_file:
            json_file.write(json.dumps(json_dictionary[0], indent=2))


def rename_the_tifs(other_files, file_path, old_product_id, new_product_id):
    for files in other_files:
        rename_file(file_path + files, file_path + files.replace(old_product_id, new_product_id))

def decode_command_key_name(key_name):
    #----------------------------------------------------------------------------------------------------
    #   Quick example of what variables should contain:                                                 #
    #   key_name = "L08/2016/043/035/LC08_T2AL_043035_20160229_20171011_01_A1.tar.gz"                   #
    #   key_pieces = ["L08", "2016", "043", "035", "LC08_T2AL_043035_20160229_20171011_01_A1.tar.gz"]   #
    #   tar_file_name = "LC08_T2AL_043035_20160229_20171011_01_A1.tar.gz"                               #
    #   file_path = "LC08_T2AL_043035_20160229_20171011_01_A1/"                                         #
    #----------------------------------------------------------------------------------------------------
    key_pieces = key_name.split('/')
    tar_file_name = key_pieces[-1]
    extract_file_path = tar_file_name.replace('.tar.gz', '/')

    return tar_file_name, extract_file_path

def get_files_in_directory(directory_path, extension_filters = [""]):
    files_in_directory = []

    for files in os.listdir(directory_path):
        for extension in extension_filters:
            if files.lower().endswith(extension.lower()):
                files_in_directory.append(files)
                break

    return files_in_directory

def cog_the_product(product_file_path):
    cog_start_time = time.time()
    #Get all the TIF files from the extracted tar.gz file
    tif_files = get_files_in_directory(product_file_path, extension_filters = [".TIF"])

    #Add the file path to each element in the list of TIF files
    for x, tif_file in enumerate(tif_files):
        tif_files[x] = product_file_path + tif_file

    #Finally, COG all the TIFs in the list, done in parallel using the multiprocessing libarary
    Pool(cpu_count()*2).map(cog_a_tif, tif_files)

    cog_total_time = time.time() - cog_start_time
    print("Total COG Time: ", cog_total_time)


#TODO: Need to split this function up more
def extract_product_metadata(product_file_path):
    metadata_start_time = time.time()

    all_files = get_files_in_directory(product_file_path)
    xml_files, odl_files, other_files = seperate_files(all_files)

    json_dictionaries = xml_to_dictionary_converter(xml_files, product_file_path)
    json_dictionaries = json_dictionaries + odl_to_dictionary_converter(odl_files, product_file_path)
    scene_metadata, primary_path, old_product_id, new_product_id = parse_metadata(json_dictionaries)
    save_the_metadata(json_dictionaries, old_product_id, new_product_id, product_file_path)

    product_dictionary = decode_product_id(new_product_id)

    new_key_path = product_dictionary["satellite"] + '/' +  product_dictionary["acquisition_year"] + '/' + product_dictionary["WRS_path"] + '/' + product_dictionary["WRS_row"] + '/' + product_dictionary["product_id"] + '/'

    if(old_product_id):
        rename_the_tifs(other_files, product_file_path, old_product_id, new_product_id)

    metadata_total_time = time.time() - metadata_start_time
    print("Total Metadata Extraction Time: ", metadata_total_time)

    return new_key_path, product_dictionary


def upload_files_to_S3(product_file_path, new_key_path, dest_bucket_name, product_dictionary):
    upload_start_time = time.time()
    input_for_upload = get_files_in_directory(product_file_path)

    for x, files in enumerate(input_for_upload):
        new_key = new_key_path + files
        input_for_upload[x] = (product_file_path, files, new_key, dest_bucket_name, product_dictionary)

    #Upload the COG to S3 and write the md5/sha to the database and metadata, done in parallel
    Pool(cpu_count()*2).starmap(upload_and_delete, input_for_upload)

    try:
        os.rmdir(product_file_path)

    except:
        exit()

    upload_total_time = time.time() - upload_start_time
    print("Total Upload Time: ", upload_total_time)

def main():
    #Record start time of program
    start_time = time.time()

    #Get the required command line arguments from the user
    source_bucket_name, dest_bucket_name, key_name = get_command_line_arguments()
    tar_file_name, extract_file_path = decode_command_key_name(key_name)

    download_object_from_s3(source_bucket_name, key_name, tar_file_name)
    extract_tar_file(tar_file_name, extract_file_path)

    cog_the_product(extract_file_path)

    new_key_path, product_dictionary = extract_product_metadata(extract_file_path)

    upload_files_to_S3(extract_file_path, new_key_path, dest_bucket_name, product_dictionary)

    total_time = time.time() - start_time
    print("Total Run Time: ", total_time)


if __name__ == '__main__':
	#Libraries required for the program
    import time, sys, os, tarfile, boto3, sha_the_file, errno, datetime, json, io, xmltodict, ast
    from multiprocessing.dummy import Pool
    from multiprocessing import cpu_count

    #Declare service resources used in program
    s3 = boto3.client('s3')
    s3_resource = boto3.resource('s3')

    #Call the default main function of the program
    main()

