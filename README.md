# cfstep-paclair [![Codefresh build status]( https://g.codefresh.io/api/badges/pipeline/codefresh-inc/codefresh-contrib%2Fcfstep-paclair%2Fcfstep-paclair?branch=master&type=cf-1)]( https://g.codefresh.io/repositories/codefresh-contrib/cfstep-paclair/builds?filter=trigger:build;branch:master;service:5bbe7af8a3686e081e4e1b91~cfstep-paclair)

Custom Docker image to support clair image scanning from Codefresh pipeline

### Prerequisites:

Codefresh Subscription - https://codefresh.io/

Running Clair Instance -
Helm Chart is available to install here: https://github.com/coreos/clair/tree/master/contrib/helm

### Documentation:

paclair: https://github.com/yebinama/paclair

### Full List of Options

To use an ENVIRONMENT VARIABLE you need to add the variables to your Codefresh Pipeline and also to your codefresh.yml.

Example `codefresh.yml` build is below with required ENVIRONMENT VARIABLES in place.

| ENVIRONMENT VARIABLE | DEFAULT | TYPE | REQUIRED | DESCRIPTION |
|----------------------------|----------|---------|----------|---------------------------------------------------------------------------------------------------------------------------------|
| CF_ACCOUNT | null | string | No | Codefresh Account Name |
| CLAIR_URL | null | string | Yes | https://clair.domain.com:6060 |
| IMAGE | null | string | Yes | Docker Image Name |
| REGISTRY_PASSWORD | null | string | Yes | Docker Registry Password |
| REGISTRY_USERNAME | null | string | Yes | Docker Registry Username |
| TAG | null | string | Yes | Docker Image Tag |

Right now this is limited to Codefresh Docker Registry.
Username is your Codefresh Username and Docker Registry keys can be created here https://g.codefresh.io/user/settings

### codefresh.yml

Codefresh Build Step to execute Twistlock scan.
All `${{var}}` variables must be put into Codefresh Build Parameters
codefresh.yml

``` console
version: '1.0'
steps:
  BuildingDockerImage:
    title: Building Docker Image
    type: build
    image_name: codefresh/demochat # Replace with your Docker image name
    working_directory: ./
    dockerfile: Dockerfile
    tag: '${{CF_BRANCH_TAG_NORMALIZED}}'
  CheckClair:
    image: codefresh/cfstep-paclair:3.0.0
    environment:
      - CF_ACCOUNT=dustinvanbuskirk
      - IMAGE=example-voting-app/worker # Replace with your Docker image name
      - TAG=${{CF_BRANCH_TAG_NORMALIZED}}
    on_success: # Execute only once the step succeeded
      metadata: # Declare the metadata attribute
        set: # Specify the set operation
          - ${{BuildingDockerImage.imageId}}: # Select any number of target images
            - SECURITY_SCAN: true
    on_fail: # Execute only once the step failed
      metadata: # Declare the metadata attribute
        set: # Specify the set operation
          - ${{BuildingDockerImage.imageId}}: # Select any number of target images
            - SECURITY_SCAN: false
  ArchiveReport:
    image: mesosphere/aws-cli
    commands:
      - aws s3 cp ./reports/clair-scan-example-voting-app-worker-${{CF_BRANCH_TAG_NORMALIZED}}.html s3://${{S3_BUCKETNAME}}/${{CF_BUILD_ID}}/clair-scan-example-voting-app-worker-${{CF_BRANCH_TAG_NORMALIZED}}.html --acl public-read
    on_success:
     metadata:
        set:
          - ${{BuildingDockerImage.imageId}}:
              - CLAIR_REPORT: "https://s3.amazonaws.com/${{S3_BUCKETNAME}}/${{CF_BUILD_ID}}/clair-scan-example-voting-app-worker-${{CF_BRANCH_TAG_NORMALIZED}}.html"
```

Optional Storage Step Variables:

| ENVIRONMENT VARIABLE | DEFAULT | TYPE | REQUIRED | DESCRIPTION |
|----------------------------|----------|---------|----------|---------------------------------------------------------------------------------------------------------------------------------|
| AWS_ACCESS_KEY_ID | null | string | No | AWS Access Key of S3 Bucket |
| AWS_DEFAULT_REGION | null | string | Yes | AWS Region of S3 Bucket |
| AWS_SECRET_ACCESS_KEY | null | string | Yes | AWS Secret Key of S3 Bucket |
| S3_BUCKETNAME | null | string | Yes | Name of S3 Bucket to Store Reports |

