import oci
from Modules.database_functions import *
from datetime import date
import time
WaitRefresh = 5

vpus = ["Unknown performance"] * 30
vpus[0] = "Lower Cost"
vpus[10] = "Balanced"
vpus[20] = "Higher Performance"

def GetVolumes(acc, config, auth, region, tenancy, compartments):
    config["region"] = region
    search = oci.resource_search.ResourceSearchClient(config, signer=auth)
    details = oci.resource_search.models.StructuredSearchDetails()
    details.matching_context_type = "NONE"
    details.query = "query volume resources"
    compute = oci.core.ComputeClient(config, signer=auth)
    blockstorage = oci.core.BlockstorageClient(config, signer=auth)
    objects = oci.pagination.list_call_get_all_results(search.search_resources, search_details=details).data

    for object in objects:
            if object.lifecycle_state.upper() != "TERMINATED":
                retry = True
                while retry:
                    retry = False
                    try:
                        detail = blockstorage.get_volume(volume_id=object.identifier).data
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
                        domain, item.Owner = mantags["CreatedBy"].split("/")
                    except:
                        item.Owner = mantags["CreatedBy"]
                except:
                    item.Owner = "Unknown"
                item.Service = "Blockstorage"

                item.ServiceDetail = "Volume performance: {} - AutoTune: {}".format(vpus[int(detail.vpus_per_gb)], detail.is_auto_tune_enabled)
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

                retry = True
                while retry:
                    retry = False
                    try:
                        detail2 = compute.list_volume_attachments(compartment_id=detail.compartment_id, volume_id=detail.id).data
                    except oci.exceptions.ServiceError as ex:
                        if ex.status == 429:
                            print ("API limiting...delaying..")
                            time.sleep(WaitRefresh)
                            retry = True
                        else:
                            print("Error with object - detail2: {} - {}".format(object.identifier, ex.message))
                            break

                master = ""
                for d2 in detail2:
                    master = d2.instance_id + ","
                master = master.rstrip(",")

                if len(detail2) == 0:
                    item.ServiceDetail = "UNATTACHED Volume! {}".format(item.ServiceDetail)

                item.MasterResource = master
                # item.CPU = 0
                # item.GPU = 0
                # item.Memory = 0
                # item.LocalStorage = 0
                item.AttachedStorage = int(detail.size_in_gbs)

                item.SaveItem()


def GetBootVolumes(acc, config, auth, region, tenancy, compartments):
    config["region"] = region
    search = oci.resource_search.ResourceSearchClient(config, signer=auth)
    details = oci.resource_search.models.StructuredSearchDetails()
    details.matching_context_type = "NONE"
    details.query = "query bootvolume resources"
    compute = oci.core.ComputeClient(config, signer=auth)
    blockstorage = oci.core.BlockstorageClient(config, signer=auth)
    objects = oci.pagination.list_call_get_all_results(search.search_resources, search_details=details).data

    for object in objects:
            if object.lifecycle_state.upper() != "TERMINATED":
                retry = True
                while retry:
                    retry = False
                    try:
                        detail = blockstorage.get_boot_volume(boot_volume_id=object.identifier).data
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
                        domain, item.Owner = mantags["CreatedBy"].split("/")
                    except:
                        item.Owner = mantags["CreatedBy"]
                except:
                    item.Owner = "Unknown"
                item.Service = "Blockstorage"

                item.ServiceDetail = "Volume performance: {} - AutoTune: {}".format(vpus[int(detail.vpus_per_gb)], detail.is_auto_tune_enabled)
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

                retry = True
                while retry:
                    retry = False
                    try:
                        detail2 = compute.list_boot_volume_attachments(compartment_id=detail.compartment_id, availability_domain=object.availability_domain, boot_volume_id=detail.id).data
                    except oci.exceptions.ServiceError as ex:
                        if ex.status == 429:
                            print ("API limiting...delaying..")
                            time.sleep(WaitRefresh)
                            retry = True
                        else:
                            print("Error with object - detail2: {} - {}".format(object.identifier, ex.message))
                            break

                # Disk NOT attached to a instance
                print ("Boot volume {} total attachments: {}".format(detail.display_name, len(detail2)))
                if len(detail2) == 0:
                    item.ServiceDetail = "UNATTACHED Bootvolume! {}".format(item.ServiceDetail)
                    item.MasterResource = ""
                    item.AttachedStorage = int(detail.size_in_gbs)

                    item.SaveItem()



