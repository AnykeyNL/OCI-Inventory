from Modules.IAM import *
from Modules.instances import *
from Modules.database_functions import *
from Modules.Volumes import *

import oci

Accounts = GetAccounts()

for acc in Accounts:
    if acc.Enabled:
        configfile = "~/.oci/config_empty"
        config = oci.config.from_file(configfile)
        config["user"] = acc.user
        config["fingerprint"] = acc.fingerprint
        config["tenancy"] = acc.tenancy
        config["region"] = acc.homeregion

        auth = oci.signer.Signer(tenancy=acc.tenancy, user=acc.user, fingerprint=acc.fingerprint, private_key_file_location=None, private_key_content=acc.key)
        identity = oci.identity.IdentityClient(config, signer=auth)

        tenancy = identity.get_tenancy(tenancy_id=acc.tenancy).data
        user = identity.get_user(acc.user).data
        print("Logged in {} as: {} @ {}".format(tenancy.name, user.description, acc.homeregion))

        print ("Checking available regions...")
        regions=SubscribedRegions(config, auth)

        print ("Getting all Compartments...")
        compartments = GetAllCompartments(config, auth)

        for region in regions:
            print ("Getting instances...")
            GetInstances(acc, config, auth, region, tenancy, compartments)
            print ("Getting blockstorage volumes...")
            GetVolumes(acc, config, auth, region, tenancy, compartments)
            print("Getting unattached boot volumes...")
            GetBootVolumes(acc, config, auth, region, tenancy, compartments)



