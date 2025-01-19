document.addEventListener('DOMContentLoaded', function () {
    const numberFields = document.querySelectorAll('.form-number');

    numberFields.forEach(function (field) {
        field.addEventListener('input', function (event) {
            let value = event.target.value.replace(/,/g, ''); // Remove existing commas

            // Allow only numbers and a single decimal point
            if (!isNaN(value) || value === '' || value === '.') {
                if (value.split('.').length > 2) {
                    // Prevent more than one decimal point
                    event.target.value = value.slice(0, -1);
                    return;
                }

                // Format the value with commas
                const parts = value.split('.'); // Split into integer and decimal parts
                parts[0] = Number(parts[0]).toLocaleString('en-US'); // Add commas to integer part
                event.target.value = parts.join('.'); // Rejoin integer and decimal parts
            } else {
                // If invalid input, reset the value to the previous valid value
                event.target.value = event.target.value.slice(0, -1);
            }
        });
    });
});

function reverseFormattedNumber(formattedValue) {
    if (!formattedValue) {
        return ''; // Return an empty string for empty input
    }

    // Remove commas from the formatted value
    const plainValue = formattedValue.replace(/,/g, '');

    // Convert to a number and ensure two decimal places
    const numericValue = parseFloat(plainValue).toFixed(2);

    // Handle cases where the input isn't a valid number
    if (isNaN(numericValue)) {
        return ''; // Return an empty string for invalid input
    }

    return numericValue; // Return the plain numeric value as a string
}

// wallet form
document.querySelector('.wallet_form').addEventListener('submit', function (event) {
    const numberFields = document.querySelectorAll('.form-number');
    numberFields.forEach(function (field) {
        field.value = reverseFormattedNumber(field.value); // Reverse formatting
        console.log(field.value);
    });
});

// edit wallet form
document.addEventListener('submit', function (event) {
    if (event.target && event.target.matches('.edit_wallet_form')) {
        console.log('edit_wallet_form submit triggered');
        const numberFields = event.target.querySelectorAll('.form-number');
        numberFields.forEach(function (field) {
            field.value = reverseFormattedNumber(field.value); // Reverse formatting
        });
    }
});

// first time transaction form
document.querySelector('.trans-modal').addEventListener('submit', function (event) {
    const numberFields = document.querySelectorAll('.form-number');
    console.log(numberFields);
    numberFields.forEach(function (field) {
        field.value = reverseFormattedNumber(field.value); // Reverse formatting
        console.log(field.value);
    });
});


// edit transaction form reverce formating
document.addEventListener('submit', function (event) {
    if (event.target && event.target.matches('.edit-trans-modal')) {
        console.log('edit-trans-modal submit triggered');
        const numberFields = event.target.querySelectorAll('.form-number');
        numberFields.forEach(function (field) {
            field.value = reverseFormattedNumber(field.value); // Reverse formatting
        });
    }
});

// transfer form reverce formatting
document.querySelector('.transfer-modal').addEventListener('submit', function (event) {
    const numberFields = document.querySelectorAll('.form-number');
    numberFields.forEach(function (field) {
        field.value = reverseFormattedNumber(field.value); // Reverse formatting
        console.log(field.value);
    });
});