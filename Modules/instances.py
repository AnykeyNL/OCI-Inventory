import oci
from Modules.database_functions import *
from datetime import date
import time
WaitRefresh = 10

def GetInstances(acc, config, auth, region, tenancy, compartments):
    config["region"] = region
    search = oci.resource_search.ResourceSearchClient(config, signer=auth)
    details = oci.resource_search.models.StructuredSearchDetails()
    details.matching_context_type = "NONE"
    details.query = "query instance resources"
    compute = oci.core.ComputeClient(config, signer=auth)
    blockstorage = oci.core.BlockstorageClient(config, signer=auth)
    objects = oci.pagination.list_call_get_all_results(search.search_resources, search_details=details).data

    for object in objects:
        if object.lifecycle_state.upper() != "TERMINATED":
            retry = True
            while retry:
                retry = False
                try:
                    detail = compute.get_instance(instance_id=object.identifier).data
                except oci.exceptions.ServiceError as ex:
                    if ex.status == 429:
                        print("API limiting...delaying..")
                        time.sleep(WaitRefresh)
                        retry = True
                    else:
                        print ("Error with object: {} - {}".format(object.identifier, ex.message))
                        break
            item = InventoryObject()
            item.cloud = "Oracle"
            item.Account = tenancy.name
            item.Region = region
            item.InventoryDate = "{}".format(date.today())
            item.CreatedDate = detail.time_created
            item.State = detail.lifecycle_state
            try:
                deftags = detail.defined_tags
                mantags = deftags[acc.CreatedByKey]
                try:
                    domain,item.Owner = mantags["CreatedBy"].split("/")
                except:
                    item.Owner = mantags["CreatedBy"]
            except:
                item.Owner = "Unknown"
            item.Service = "Compute"
            item.ServiceDetail = "{} - {}".format(detail.shape, detail.shape_config.processor_description)
            item.Name = detail.display_name
            item.ServiceID = detail.id
            for compartment in compartments:
                if compartment.details.id == detail.compartment_id:
                    item.Location = compartment.fullpath
                    try:
                        deftags = compartment.details.defined_tags
                        mantags = deftags[acc.CreatedByKey]
                        try:
                            domain, item.LocationOwner = mantags["CreatedBy"].split("/")
                        except:
                            item.LocationOwner = mantags["CreatedBy"]
                    except:
                        item.LocationOwner = "Unknown"
                        break
                    break
            item.MasterResource = detail.id
            item.CPU = int(detail.shape_config.ocpus)
            item.GPU = int(detail.shape_config.gpus)
            item.Memory = int(detail.shape_config.memory_in_gbs)
            try:
                item.LocalStorage = int(detail.shape_config.local_disks_total_size_in_gbs)
            except:
                item.LocalStorage = 0

            retry = True
            while retry:
                retry = False
                try:
                    bootvolumes = compute.list_boot_volume_attachments(availability_domain=detail.availability_domain, compartment_id=detail.compartment_id, instance_id=detail.id).data
                except oci.exceptions.ServiceError as ex:
                    if ex.status == 429:
                        print("API limiting...delaying..")
                        time.sleep(WaitRefresh)
                        retry = True
                    else:
                        print ("Error with object - bootvols: {} - {}".format(object.identifier, ex.message))
                        break

            AttachedStorage = 0
            for bootvolume in bootvolumes:
                retry = True
                while retry:
                    retry = False
                    try:
                        bootvolumedetail = blockstorage.get_boot_volume(boot_volume_id=bootvolume.boot_volume_id).data
                    except oci.exceptions.ServiceError as ex:
                        if ex.status == 429:
                            print("API limiting...delaying..")
                            time.sleep(WaitRefresh)
                            retry = True
                        else:
                            print("Error with object - bootvols: {} - {}".format(object.identifier, ex.message))
                            break

                AttachedStorage = int(AttachedStorage + int(bootvolumedetail.size_in_gbs))

            item.AttachedStorage = AttachedStorage

            item.SaveItem()





