import h5py


def main():
    row_number = 0

    with h5py.File('test-file-generator/val_data.h5', 'r') as f:
        dataset = f['data'][:]

        # Get the first row
        row = dataset[row_number]

    with h5py.File('row_0_data.h5', 'w') as f_out:
        # Create a dataset with the same dtype, wrapped in a list to keep it 2D if needed
        f_out.create_dataset('data', data=[row])

    with h5py.File('test-file-generator/val_label.h5', 'r') as f:
        labels = f['label'][:]

        # Get the first row
        print(f"actual label: {labels[row_number]}")
        

if __name__ == '__main__':
    main()