# Sparse Checkout Guide

This guide outlines the steps to perform a sparse checkout of specific directories from a GitHub repository.

## Steps

1. **Navigate to the Desired Directory**
    ```bash
    cd path/to/your/working/directory
    ```

2. **Initialize a New Git Repository**
    ```bash
    git init your-submodule-folder
    cd your-submodule-folder
    ```

3. **Add the Remote Repository**
    ```bash
    git remote add -f origin https://github.com/bogovicj/ngff.git
    ```

4. **Enable Sparse Checkout**
    ```bash
    git config core.sparseCheckout true
    ```

5. **Configure Sparse Checkout Paths**
    - Open the sparse-checkout configuration file:
      ```bash
      vim .git/info/sparse-checkout
      ```
    - Add the paths of the directories you want to include:
      ```plaintext
      coord-transforms/0.6-dev/examples
      another-directory/path
      yet-another-directory/path
      ```

6. **Pull the Specified Branch**
    ```bash
    git pull origin coord-transforms
    ```

7. **Update Working Directory**
    ```bash
    git read-tree -mu HEAD
    ```

## Additional Notes

-  To add more directories, simply edit the `.git/info/sparse-checkout` file and repeat steps 6 and 7.
-  Ensure the paths in the sparse-checkout file are relative to the repository root.

This setup allows you to efficiently manage which parts of a repository you want to include in your local clone without needing to download the entire repository.
