import os
import json
import uuid
from zipfile import ZipFile

from tvb.adapters.uploaders.csv_connectivity_importer import CSVConnectivityImporterModel
from tvb.adapters.uploaders.csv_connectivity_importer import CSVDelimiterOptionsEnum
from tvb.basic.logger.builder import get_logger
from tvb.interfaces.rest.client.examples.utils import compute_tvb_data_path, monitor_operation, compute_rest_url
from tvb.interfaces.rest.client.tvb_client import TVBClient
from tvb.adapters.uploaders.csv_connectivity_importer import CSVConnectivityImporter, CSVConnectivityImporterForm
from tvb.adapters.uploaders.bids_importer import BIDSImporter, BIDSImporterModel, BIDSUploadDataTypeOptionsEnum



root_dir = 'BIDS_DEMO_DATSET - Copy'

sub_dir = root_dir + '/sub-01'

algs_dir = os.listdir(sub_dir)

model_mapper = {
    'coord': None,
    'net' : CSVConnectivityImporterModel(),
    'spatial': None,
    'ts': None
}

possible_paths = {
    BIDSUploadDataTypeOptionsEnum.SURFACE: [],
    BIDSUploadDataTypeOptionsEnum.CONNECTIVITY: ["CoordsRows", "CoordsColumns"],
    BIDSUploadDataTypeOptionsEnum.FUNCTIONAL_CONNECTIVITY: ["CoordsRows", "CoordsColumns", "ModelEq", "ModelParam", "Network"],
    BIDSUploadDataTypeOptionsEnum.TIME_SERIES: ["CoordsRows", "CoordsColumns", "ModelEq", "ModelParam", "Network"]
}

delimiter_mapper = {
    ' ': CSVDelimiterOptionsEnum.SPACE
}

def filter(arr, sub_str):
    return [file_name for file_name in arr if sub_str in file_name]


# print(os.listdir(sub_dir))

def create_archive(files_list, zip_name, base_dir):
    base_dir_name = os.path.dirname(base_dir)
    with ZipFile(zip_name, 'w') as myzip:
        for file_name in files_list:
            myzip.write(file_name, arcname=file_name.split(base_dir_name)[1])


def upload_bids_data(tvb_client_instance):
    projects_of_user = tvb_client_instance.get_project_list()
    assert len(projects_of_user) > 0

    project_gid = projects_of_user[0].gid

    print(project_gid)
    print(projects_of_user[0].name)

    model = BIDSImporterModel()

    model.uploaded = "C:/Users/upadh/Documents/GitHub/tvb-root/tvb_framework/tvb/interfaces/rest/client/examples/BIDS_DEMO_DATA_SET.zip"
    model.bids_file_upload_type = BIDSUploadDataTypeOptionsEnum.CONNECTIVITY

    operation_gid = tvb_client_instance.launch_operation(project_gid, BIDSImporter,
                                                         model)
    monitor_operation(tvb_client_instance, operation_gid)

    print("Get the result of import...")
    connectivity_dto = tvb_client_instance.get_operation_results(operation_gid)[0]

    print(connectivity_dto)

def filter(arr, sub_str):
    return [file_name for file_name in arr if sub_str in file_name]

def create_bids_dataset(bids_data_to_import, bids_root_dir, bids_file_base_dir, bids_file_name):
    SUBJECT_PREFIX = 'sub'
    temp_bids_dir_name = bids_file_name + '-' + str(uuid.uuid4()).split("-")[4]
    temp_bids_dir = bids_file_base_dir + '/' + temp_bids_dir_name
    print(temp_bids_dir)
    temp_bids_zip_dir = temp_bids_dir + '.zip'

    if True:
        # read the connectivity folder and all its dependenies from json file
        # and create a zip to upload
        files = os.listdir(bids_root_dir)
        subject_folders = []
        # First we find subject parent folders
        for file_name in files:
            if os.path.basename(file_name).startswith(SUBJECT_PREFIX) and os.path.isdir(bids_root_dir + '/' + file_name):
                subject_folders.append(file_name)
        
        print(subject_folders)

        for sub in subject_folders:
            sub_contents_path = bids_root_dir + '/' + sub + '/' + bids_data_to_import.value
            sub_contents = os.listdir(sub_contents_path)
            if len(sub_contents) == 0:
                continue

           # 1. define a set to gather all necessary file paths in memory
            files_to_archive = set()

            # 2. add all file paths from the selected folder in set
            for file_name in os.listdir(sub_contents_path):
                files_to_archive.add(os.path.join(sub_contents_path, file_name))
            print(files_to_archive)

            # 3. reading json files present in the sub_contents path
            print(sub_contents)
            json_files = filter(sub_contents, '.json')
            print(json_files)

            import_dependencies_paths = set()
            json_files_processed = {}

            print("possinblekey paths")

            print(possible_paths[bids_data_to_import])

            for file in json_files:
                try:
                    file_info = json.load(open(sub_contents_path + '/' + file))
                    # print(file_info)
                    for possible_path_key in possible_paths[bids_data_to_import]:
                        if isinstance(file_info[possible_path_key], list):
                            for path in file_info[possible_path_key]:
                                import_dependencies_paths.add(path)
                        else:
                            import_dependencies_paths.add(file_info[possible_path_key])
                except Exception as e:
                    print("error occ")
                    print(e)
            
            print(import_dependencies_paths)
            print("--==")
            # print(temp_bids_dir_name)
            

            print("=============================================")

            for dependency_path in import_dependencies_paths:
                print(dependency_path)
                # print(json.load(open(bids_root_dir + '/' + dependency_path)))
                abs_path = file_path_creator(bids_root_dir, sub, dependency_path)
                print(abs_path)

                try:
                    json_data = json.load(open(file_path_creator(bids_root_dir, sub, dependency_path)))
                    print(json_data)
                    # Add json links to the files_to_archive set
                    files_to_archive.add(abs_path)

                except Exception as e:
                    print(e)

                print("------------------------------------------")

            # Finally, create an archive with all file paths in the files_to_archive set
            create_archive(files_to_archive, temp_bids_zip_dir, bids_root_dir)


def file_path_creator(bids_root_dir, sub, path):
    if '../..' in path:
        path = path.replace('../..', bids_root_dir)
    elif '..' in path:
        path = path.replace('..', bids_root_dir + '/' + sub)
    return path







if __name__ == '__main__':
    # tvb_client = TVBClient(compute_rest_url())
    # tvb_client.browser_login()
    # upload_bids_data(tvb_client)
    bids_file_base_dir = "C:/Users/upadh/Documents/GitHub/tvb-root/tvb_framework/tvb/interfaces/rest/client/examples"
    bids_root_dir = os.path.join(bids_file_base_dir, "BIDS_DEMO_DATSET - Copy")
    create_bids_dataset(BIDSUploadDataTypeOptionsEnum.TIME_SERIES, bids_root_dir, bids_file_base_dir, "BIDS_DEMO_DATSET - Copy")