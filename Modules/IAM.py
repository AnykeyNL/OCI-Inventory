import oci
import time
from Modules.Classes import *


WaitRefresh = 10


def SubscribedRegions(config, auth):
    regions = []
    identity = oci.identity.IdentityClient(config, signer=auth)
    regionDetails = identity.list_region_subscriptions(tenancy_id=config["tenancy"]).data
    # Add subscribed regions to list
    for detail in regionDetails:
        regions.append(detail.region_name)
    return regions


# class OCICompartments:
#     fullpath = ""
#     details = oci.identity.models.Compartment()

def GetCompartments(identity, rootID):
    retry = True
    while retry:
        retry = False
        try:
            #print ("Getting compartments for {}".format(rootID))
            compartments = oci.pagination.list_call_get_all_results(identity.list_compartments, compartment_id=rootID).data
            return compartments
        except Exception as e:
            if e.status == 429:
                print ("API busy.. retry")
                retry = True
                time.sleep(WaitRefresh)
            print ("bad error!")

    return []


def GetAllCompartments(config, auth):
    startcomp = config["tenancy"]
    c = []
    identity = oci.identity.IdentityClient(config, signer=auth)

    # Adding root compartment
    compartment = identity.get_compartment(compartment_id=startcomp).data
    newcomp = OCICompartments()
    newcomp.details = compartment
    newcomp.fullpath = "\\root"
    c.append(newcomp)

    # Add first level subcompartments
    compartments = GetCompartments(identity, startcomp)

    # Add 2nd level subcompartments
    fullpath = "/"
    for compartment in compartments:
        if compartment.lifecycle_state == "ACTIVE":
            newcomp = OCICompartments()
            newcomp.details = compartment
            newcomp.fullpath = "{}{}".format(fullpath, compartment.name)
            c.append(newcomp)
            subcompartments = GetCompartments(identity, compartment.id)
            subpath1 = compartment.name
            for sub1 in subcompartments:
                if sub1.lifecycle_state == "ACTIVE":
                    newcomp = OCICompartments()
                    newcomp.details = sub1
                    newcomp.fullpath = "{}{}/{}".format(fullpath, subpath1, sub1.name)
                    c.append(newcomp)

                    subcompartments2 = GetCompartments(identity, sub1.id)
                    subpath2 = sub1.name
                    for sub2 in subcompartments2:
                        if sub2.lifecycle_state == "ACTIVE":
                            newcomp = OCICompartments()
                            newcomp.details = sub2
                            newcomp.fullpath = "{}{}/{}/{}".format(fullpath, subpath1, subpath2, sub2.name)
                            c.append(newcomp)

                            subcompartments3 = GetCompartments(identity, sub2.id)
                            subpath3 = sub2.name
                            for sub3 in subcompartments3:
                                if sub3.lifecycle_state == "ACTIVE":
                                    newcomp = OCICompartments()
                                    newcomp.details = sub3
                                    newcomp.fullpath = "{}{}/{}/{}/{}".format(fullpath, subpath1, subpath2, subpath3, sub3.name)
                                    c.append(newcomp)

                                    subcompartments4 = GetCompartments(identity, sub3.id)
                                    subpath4 = sub3.name
                                    for sub4 in subcompartments4:
                                        if sub4.lifecycle_state == "ACTIVE":
                                            newcomp = OCICompartments()
                                            newcomp.details = sub
                                            newcomp.fullpath = "{}{}/{}/{}/{}/{}".format(fullpath, subpath1, subpath2,
                                                                                         subpath3, subpath4, sub4.name)
                                            c.append(newcomp)

                                            subcompartments5 = GetCompartments(identity, sub4.id)
                                            subpath5 = sub4.name
                                            for sub5 in subcompartments5:
                                                if sub5.lifecycle_state == "ACTIVE":
                                                    newcomp = OCICompartments()
                                                    newcomp.details = sub5
                                                    newcomp.fullpath = "{}{}/{}/{}/{}/{}/{}".format(fullpath,
                                                                                                         subpath1,
                                                                                                         subpath2,
                                                                                                         subpath3,
                                                                                                         subpath4,
                                                                                                         subpath5,
                                                                                                         sub5.name)
                                                    c.append(newcomp)

                                                    subcompartments6 = GetCompartments(identity, sub5.id)
                                                    subpath6 = sub5.name
                                                    for sub6 in subcompartments6:
                                                        if sub6.lifecycle_state == "ACTIVE":
                                                            newcomp = OCICompartments()
                                                            newcomp.details = sub6
                                                            newcomp.fullpath = "{}{}/{}/{}/{}/{}/{}/{}".format(
                                                                fullpath,
                                                                subpath1,
                                                                subpath2,
                                                                subpath3,
                                                                subpath4,
                                                                subpath5, subpath6,
                                                                sub6.name)
                                                            c.append(newcomp)

    return c

