import json
import yaml
import os
import re
import requests
import sys
import subprocess
import time

def run_command(full_command):
    proc = subprocess.Popen(full_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output = proc.communicate()
    print(output)
    if proc.returncode != 0:
        sys.exit(1)
    return b''.join(output).strip().decode()  # only save stdout into output, ignore stderr

def create_annotation_list(json_data):
    annotations = []
    annotation_list = ''
    for key, value in json_data.items():
        annotations.append("-l CLAIR_VULNS_{}={}".format(key.upper(), value))
        annotation_list = ' '.join(annotations)
    return annotation_list


def annotate_image(docker_image_id, annotation_list):

    annotate_image_exec = ("codefresh annotate image {} {}"
                           .format(docker_image_id,
                                   annotation_list
                                   )
                           )

    run_command(annotate_image_exec)


def main(command):
    cf_account = os.getenv('CF_ACCOUNT')
    clair_url = os.getenv('CLAIR_URL', 'http://clair:6060')
    clair_verify = os.getenv('CLAIR_VERIFY', 'false')
    image = os.getenv('IMAGE')
    tag = os.getenv('TAG')
    registry = os.getenv('REGISTRY', 'r.cfcr.io') 
    registry_username = os.getenv('REGISTRY_USERNAME')
    registry_password = os.getenv('REGISTRY_PASSWORD')

    # Build paclair config

    data = {
                'General': {
                    'clair_url':clair_url, 
                    'verify':clair_verify
                },
                'Plugins': {
                    'Docker': {
                        'class': 'paclair.plugins.docker_plugin.DockerPlugin',
                        'registries': { 
                            registry: {
                                'auth': [
                                    registry_username,
                                    registry_password
                                ]
                            }
                        }
                    }
                }
            }

    with open('/etc/paclair.conf', 'w') as outfile:
        yaml.dump(data, outfile, default_flow_style=False)

    if cf_account:
        full_registry = '/'.join([registry, cf_account])
    else:
        full_registry = registry
    
    docker_image_id = '{}:{}'.format(image, tag)

    base_command = ("paclair Docker {}/{}:{}"
                        .format(
                                full_registry,
                                image,
                                tag
                                )
                        )
    
    if command == 'scan':
        command_array = ['push', 'analyse --output-format html', 'analyse --output-format stats', 'delete']
        for command in command_array:
            if 'stats' in command:
                if cf_account:
                    output = run_command(' '.join([base_command, command]))
                    l = output.strip().split('\n')
                    json_data = {i.strip().split(':')[0]: int(i.strip().split(':')[1]) for i in l}
                    annotations = create_annotation_list(json_data)
                    annotate_image(docker_image_id, annotations)
                else:
                    output = run_command(' '.join([base_command, command]))
                    print(output)
            if 'html' in command:
                if not os.path.exists('reports'):
                    os.makedirs('reports')
                output = run_command(' '.join([base_command, command]))
                report_name = 'clair-scan-{}-{}.html'.format(image.replace('/', '-'), tag)
                with open('reports/{}'.format(report_name), 'w') as f:
                    f.write(str(output))
                    f.close()
            else:
                output = run_command(' '.join([base_command, command]))
                print(output)
    else: 
        output = run_command(' '.join([base_command, command]))
        print(output)

if __name__ == "__main__":
    main(sys.argv[1])
