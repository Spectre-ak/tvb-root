import os
import json

from tvb.adapters.uploaders.csv_connectivity_importer import CSVConnectivityImporterModel
from tvb.adapters.uploaders.csv_connectivity_importer import CSVDelimiterOptionsEnum

from tvb.adapters.analyzers.bct_adapters import BaseBCTModel
from tvb.adapters.analyzers.bct_degree_adapters import Degree
from tvb.adapters.uploaders.region_mapping_importer import RegionMappingImporterModel, RegionMappingImporter
from tvb.adapters.uploaders.zip_connectivity_importer import ZIPConnectivityImporterModel, ZIPConnectivityImporter
from tvb.adapters.uploaders.zip_surface_importer import ZIPSurfaceImporterModel, ZIPSurfaceImporter
from tvb.basic.logger.builder import get_logger
from tvb.datatypes.surfaces import SurfaceTypesEnum
from tvb.interfaces.rest.client.examples.utils import compute_tvb_data_path, monitor_operation, compute_rest_url
from tvb.interfaces.rest.client.tvb_client import TVBClient
from tvb.adapters.uploaders.csv_connectivity_importer import CSVConnectivityImporter, CSVConnectivityImporterForm



root_dir = 'BIDS_DEMO_DATSET - Copy'

sub_dir = root_dir + '/sub-01'

algs_dir = os.listdir(sub_dir)

model_mapper = {
    'coord': None,
    'net' : CSVConnectivityImporterModel(),
    'spatial': None,
    'ts': None
}

delimiter_mapper = {
    ' ': CSVDelimiterOptionsEnum.SPACE
}

def filter(arr, sub_str):
    return [file_name for file_name in arr if sub_str in file_name]


print(os.listdir(sub_dir))

def launch_operation_examples(tvb_client_instance):
    projects_of_user = tvb_client_instance.get_project_list()
    assert len(projects_of_user) > 0
    
    project_gid = projects_of_user[0].gid

    print(project_gid)
    print(projects_of_user[0].name)

    for alg in algs_dir:
        alg_model = model_mapper[alg]
        if alg_model is not None:
            print('fpind')
            
            model_data_path = sub_dir + '/' + alg
            model_data_files = os.listdir(model_data_path)
            csv_files = filter(model_data_files, '.tsv')
            json_files = filter(model_data_files, '.json')
            
            distances_data = filter(csv_files, '_distances')
            weights_data = filter(csv_files, '_weights')

            distances_json = filter(json_files, '_distances')
            weights_json = filter(json_files, '_weights')
            
            total_no_files = len(distances_data)
            print(distances_json[0])
    
            for i in range(total_no_files):
                print(i)
                distances_data_info = json.load(open(model_data_path + '/' + distances_json[i]))
                weights_data_info = json.load(open(model_data_path + '/' + weights_json[i]))
                
                model = model_mapper[alg]

                model.weights = model_data_path + '/' + weights_data[i]
                model.weights_delimiter = delimiter_mapper[weights_data_info['Delimiter']]
                model.tracts = model_data_path + '/' + distances_data[i]
                model.tracts_delimiter = delimiter_mapper[distances_data_info['Delimiter']]

                print("Importing a connectivity from csv...")

                operation_gid = tvb_client_instance.launch_operation(project_gid, CSVConnectivityImporter,
                                                         model)
                monitor_operation(tvb_client_instance, operation_gid)

                print("Get the result of connectivity import...")
                connectivity_dto = tvb_client_instance.get_operation_results(operation_gid)[0]

                print(connectivity_dto)

                print(distances_data_info)
                print(weights_data_info)

            
            print(json_files)
            print(csv_files)
            print(distances_data)
            print(distances_json)
            print(weights_data)
            print(weights_json)


if __name__ == '__main__':
    tvb_client = TVBClient(compute_rest_url())

    tvb_client.browser_login()
    launch_operation_examples(tvb_client)

