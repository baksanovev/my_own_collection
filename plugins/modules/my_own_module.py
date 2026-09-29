#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import os


def run_module():
    module_args = dict(
        path=dict(type='str', required=True),
        content=dict(type='str', required=True),
    )

    result = dict(
        changed=False,
        message=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    path = module.params['path']
    content = module.params['content']

    current_content = None

    if os.path.exists(path):
        try:
            with open(path, 'r') as file:
                current_content = file.read()
        except OSError as error:
            module.fail_json(
                msg=f'Failed to read file: {error}',
                **result
            )

    if current_content == content:
        result['message'] = 'File already contains the required content'
        module.exit_json(**result)

    if module.check_mode:
        result['changed'] = True
        result['message'] = 'File would be changed'
        module.exit_json(**result)

    try:
        with open(path, 'w') as file:
            file.write(content)
    except OSError as error:
        module.fail_json(
            msg=f'Failed to write file: {error}',
            **result
        )

    result['changed'] = True
    result['message'] = 'File was created or updated'

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
