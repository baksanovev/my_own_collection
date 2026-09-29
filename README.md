# Домашнее задание «Создание собственных модулей»

---

## Задание

В рамках домашнего задания был разработан собственный Ansible-модуль для создания файла с заданным содержимым.

Модуль принимает два параметра:

- `path` — путь к создаваемому файлу;
- `content` — содержимое файла.

Также была реализована идемпотентность модуля, создана Ansible Collection и роль, использующая разработанный модуль.

---

## 1. Подготовка окружения

Для выполнения задания использовалась виртуальная машина с Ubuntu.

Версии используемого ПО:

```text
Ubuntu 24.04 LTS
Python 3.12.3
Git 2.43.0
Ansible Core 2.19.13
```

Для разработки использовалась ветка Ansible:

```text
stable-2.19
```

---

## 2. Создание собственного Ansible-модуля

Был создан модуль:

```text
my_own_module.py
```

Модуль принимает два обязательных параметра:

```text
path
content
```

Код модуля:

```python
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
```

Если файл отсутствует или его содержимое отличается от требуемого, модуль создаёт или изменяет файл и возвращает:

```text
changed: true
```

Если файл уже содержит необходимые данные, модуль не выполняет изменений и возвращает:

```text
changed: false
```

Таким образом обеспечивается идемпотентность.

---

## 3. Проверка синтаксиса модуля

Перед запуском была выполнена проверка Python-кода:

```bash
python -m py_compile my_own_module.py
```

Команда завершилась без ошибок.

---

## 4. Локальное тестирование модуля

Для тестирования использовался `hacking/test-module.py`.

Перед первым запуском тестовый файл отсутствовал.

Команда:

```bash
python ~/ansible/hacking/test-module.py \
  -m ./my_own_module.py \
  -a 'path=/tmp/netology_test.txt content="Hello from my Ansible module!"'
```

При первом запуске модуль создал файл:

```json
{
    "changed": true,
    "message": "File was created or updated"
}
```

Проверка содержимого файла:

```bash
cat /tmp/netology_test.txt
```

Результат:

```text
Hello from my Ansible module!
```

### Скриншот пункта 4

<img width="1207" height="434" alt="image" src="https://github.com/user-attachments/assets/3d4fd593-f111-4d0b-b915-74016835fcd2" />


---

## 5. Проверка идемпотентности модуля

Модуль был повторно запущен с теми же параметрами:

```bash
python ~/ansible/hacking/test-module.py \
  -m ./my_own_module.py \
  -a 'path=/tmp/netology_test.txt content="Hello from my Ansible module!"'
```

Результат:

```json
{
    "changed": false,
    "message": "File already contains the required content"
}
```

Таким образом:

```text
Первый запуск  -> changed: true
Второй запуск -> changed: false
```

Идемпотентность модуля подтверждена.

---

## 6. Использование собственного модуля в Playbook

Для использования модуля через Ansible Playbook была создана директория:

```text
library/
```

Модуль был помещён в неё:

```text
library/my_own_module.py
```

Inventory:

```ini
[local]
localhost ansible_connection=local
```

Playbook:

```yaml
---
- name: Test my own Ansible module
  hosts: local
  gather_facts: false

  tasks:
    - name: Create file using my own module
      my_own_module:
        path: /tmp/netology_playbook.txt
        content: "Created by my own Ansible module!"
```

Первый запуск:

```bash
ansible-playbook -i inventory.ini playbook.yml
```

Результат:

```text
PLAY RECAP

localhost : ok=1 changed=1 unreachable=0 failed=0
```

Повторный запуск:

```bash
ansible-playbook -i inventory.ini playbook.yml
```

Результат:

```text
PLAY RECAP

localhost : ok=1 changed=0 unreachable=0 failed=0
```

Это подтверждает идемпотентность собственного модуля при использовании через Ansible Playbook.

### Скриншот пункта 6

<img width="835" height="430" alt="image" src="https://github.com/user-attachments/assets/eb4d9866-9450-4968-87f9-44529835ff86" />


---

## 7. Создание Ansible Collection

Была создана Ansible Collection:

```text
my_own_namespace.yandex_cloud_elk
```

Команда:

```bash
ansible-galaxy collection init my_own_namespace.yandex_cloud_elk
```

Разработанный модуль был помещён в:

```text
plugins/modules/my_own_module.py
```

Структура Collection:

```text
yandex_cloud_elk/
├── README.md
├── galaxy.yml
├── meta/
│   └── runtime.yml
├── plugins/
│   ├── README.md
│   └── modules/
│       └── my_own_module.py
└── roles/
    └── my_own_role/
        ├── README.md
        ├── defaults/
        │   └── main.yml
        ├── handlers/
        │   └── main.yml
        ├── meta/
        │   └── main.yml
        ├── tasks/
        │   └── main.yml
        ├── tests/
        └── vars/
            └── main.yml
```

---

## 8. Создание роли

Внутри Collection была создана роль:

```text
my_own_role
```

Команда:

```bash
ansible-galaxy role init my_own_role
```

В `roles/my_own_role/defaults/main.yml` были определены переменные:

```yaml
---
my_own_path: "/tmp/netology_collection.txt"
my_own_content: "Created by my own collection!"
```

В `roles/my_own_role/tasks/main.yml` создан вызов собственного модуля:

```yaml
---
- name: Create file using my own module
  my_own_namespace.yandex_cloud_elk.my_own_module:
    path: "{{ my_own_path }}"
    content: "{{ my_own_content }}"
```

Для обращения к модулю используется FQCN:

```text
my_own_namespace.yandex_cloud_elk.my_own_module
```

---

## 9. Настройка Collection

Основные параметры `galaxy.yml`:

```yaml
---
namespace: my_own_namespace
name: yandex_cloud_elk
version: 1.0.0
readme: README.md

authors:
  - baksanovev

description: Ansible collection with custom module and role for Netology homework

license:
  - MIT

tags:
  - netology
  - ansible

dependencies: {}

build_ignore:
  - "*.tar.gz"
```

---

## 10. Сборка Collection

Collection была собрана командой:

```bash
ansible-galaxy collection build
```

В результате был создан архив:

```text
my_own_namespace-yandex_cloud_elk-1.0.0.tar.gz
```

Проверка содержимого архива:

```bash
tar -tzf my_own_namespace-yandex_cloud_elk-1.0.0.tar.gz | \
grep -E 'my_own_module|my_own_role'
```

В архиве присутствуют собственный модуль и роль:

```text
plugins/modules/my_own_module.py
roles/my_own_role/
roles/my_own_role/defaults/main.yml
roles/my_own_role/tasks/main.yml
```

---

## 11. Публикация Collection в GitHub

Для Collection был создан отдельный публичный GitHub-репозиторий:

[my_own_collection](https://github.com/baksanovev/my_own_collection)

Collection была добавлена в Git:

```bash
git init
git branch -M main
git add .
git commit -m "Add Ansible collection with custom module and role"
```

Был подключён удалённый репозиторий:

```bash
git remote add origin git@github.com:baksanovev/my_own_collection.git
```

После этого изменения были отправлены в GitHub:

```bash
git push -u origin main
```

---

## 12. Создание версии 1.0.0

Для Collection был создан Git-тег:

```bash
git tag -a 1.0.0 -m "Release 1.0.0"
```

Проверка:

```bash
git tag
```

Результат:

```text
1.0.0
```

Тег был отправлен в GitHub:

```bash
git push origin 1.0.0
```

Результат:

```text
To github.com:baksanovev/my_own_collection.git
 * [new tag]         1.0.0 -> 1.0.0
```

Проверка состояния репозитория:

```bash
git status
git log --oneline --decorate -5
```

Результат:

```text
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean

3a5a2a0 (HEAD -> main, tag: 1.0.0, origin/main) Add Ansible collection with custom module and role
```

---

## 13. Архив Collection

В репозитории опубликован собранный архив:

[my_own_namespace-yandex_cloud_elk-1.0.0.tar.gz](https://github.com/baksanovev/my_own_collection/blob/main/my_own_namespace-yandex_cloud_elk-1.0.0.tar.gz)

Архив содержит версию Collection:

```text
1.0.0
```

---

## 14. Подготовка отдельного окружения для проверки

Для проверки собранной Collection была создана отдельная директория:

```bash
mkdir -p ~/collection-test
cd ~/collection-test
```

В неё был помещён архив:

```text
my_own_namespace-yandex_cloud_elk-1.0.0.tar.gz
```

Также были созданы `inventory.ini` и `playbook.yml`.

Inventory:

```ini
[local]
localhost ansible_connection=local
```

Playbook:

```yaml
---
- name: Test installed collection
  hosts: local
  gather_facts: false

  roles:
    - role: my_own_namespace.yandex_cloud_elk.my_own_role
```

Проверка синтаксиса:

```bash
ansible-playbook -i inventory.ini playbook.yml --syntax-check
```

Результат:

```text
playbook: playbook.yml
```

---

## 15. Установка Collection из архива

Collection была установлена непосредственно из созданного архива:

```bash
ansible-galaxy collection install \
  my_own_namespace-yandex_cloud_elk-1.0.0.tar.gz \
  --force
```

Результат:

```text
Starting galaxy collection install process
Process install dependency map
Starting collection install process

Installing 'my_own_namespace.yandex_cloud_elk:1.0.0' to '/home/baksanovev/.ansible/collections/ansible_collections/my_own_namespace/yandex_cloud_elk'

my_own_namespace.yandex_cloud_elk:1.0.0 was installed successfully
```

### Скриншот пункта 15

<img width="1062" height="216" alt="image" src="https://github.com/user-attachments/assets/2b2abb8c-dcb3-407a-ace6-9fd02775e366" />


---

## 16. Проверка установленной Collection

Перед запуском был удалён предыдущий тестовый файл:

```bash
rm -f /tmp/netology_collection.txt
```

После этого выполнен playbook:

```bash
ansible-playbook -i inventory.ini playbook.yml
```

Результат:

```text
PLAY [Test installed collection]

TASK [my_own_namespace.yandex_cloud_elk.my_own_role : Create file using my own module]

changed: [localhost]

PLAY RECAP

localhost : ok=1 changed=1 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0
```

Проверка созданного файла:

```bash
cat /tmp/netology_collection.txt
```

Результат:

```text
Created by my own collection!
```

Повторный запуск playbook:

```bash
ansible-playbook -i inventory.ini playbook.yml
```

Результат:

```text
TASK [my_own_namespace.yandex_cloud_elk.my_own_role : Create file using my own module]

ok: [localhost]

PLAY RECAP

localhost : ok=1 changed=0 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0
```

Таким образом, после установки Collection из архива собственный модуль и роль работают корректно, а повторный запуск подтверждает идемпотентность.

### Скриншот пункта 16

<img width="817" height="243" alt="image" src="https://github.com/user-attachments/assets/1fd9b131-6633-45b0-9451-d646218358e0" />


---

# Ссылки

## Репозиторий Ansible Collection

[https://github.com/baksanovev/my_own_collection](https://github.com/baksanovev/my_own_collection)

## Архив Collection 1.0.0

[my_own_namespace-yandex_cloud_elk-1.0.0.tar.gz](https://github.com/baksanovev/my_own_collection/blob/main/my_own_namespace-yandex_cloud_elk-1.0.0.tar.gz)

## Версия

```text
1.0.0
```

---

# Итог

В ходе выполнения домашнего задания:

1. Разработан собственный Ansible-модуль `my_own_module`.
2. Реализованы параметры `path` и `content`.
3. Реализована идемпотентность.
4. Выполнено локальное тестирование модуля.
5. Модуль протестирован через Ansible Playbook.
6. Создана Ansible Collection `my_own_namespace.yandex_cloud_elk`.
7. Создана роль `my_own_role`.
8. Роль использует собственный модуль через FQCN.
9. Collection собрана в архив версии `1.0.0`.
10. Исходный код Collection опубликован в GitHub.
11. Создан Git-тег `1.0.0`.
12. Collection успешно установлена из `.tar.gz`.
13. Работа установленной Collection проверена отдельным Playbook.
14. Повторный запуск подтвердил идемпотентность.
