// Initialize jQuery
$(document).ready(function() {
    // Add smooth animations
    addAnimations();
    
    // Form submission handler
    $('#loanForm').on('submit', function(e) {
        e.preventDefault();
        
        // Validate form inputs
        if (!validateForm()) {
            return;
        }
        
        // Show loading state with animation
        showLoading();
        
        // Get form data
        const formData = {
            age: $('#age').val(),
            annual_income: $('#annual_income').val(),
            monthly_expenses: $('#monthly_expenses').val(),
            old_dependents: $('#old_dependents').val(),
            young_dependents: $('#young_dependents').val(),
            occupants_count: $('#occupants_count').val(),
            house_area: $('#house_area').val(),
            loan_installments: $('#loan_installments').val(),
            type_of_house: $('#type_of_house').val(),
            sex: $('#sex').val()
        };
        
        // Make AJAX call with loading animation
        $.ajax({
            url: '/predictdata',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(response) {
                handleSuccess(response);
            },
            error: function(xhr, status, error) {
                handleError(error);
            }
        });
    });
});

// Add animations
function addAnimations() {
    // Card hover animation
    $('.prediction-card').on('mouseenter', function() {
        $(this).addClass('hover');
    }).on('mouseleave', function() {
        $(this).removeClass('hover');
    });
    
    // Button hover animation
    $('.submit-btn').on('mouseenter', function() {
        $(this).addClass('hover');
    }).on('mouseleave', function() {
        $(this).removeClass('hover');
    });
    
    // Form field focus animation
    $('.form-control, .form-select').on('focus', function() {
        $(this).addClass('focused');
    }).on('blur', function() {
        $(this).removeClass('focused');
    });
    
    // Success/error box animation
    $('.result-box').on('show.bs.collapse', function() {
        $(this).addClass('showing');
    }).on('hidden.bs.collapse', function() {
        $(this).removeClass('showing');
    });
}

// Form validation with animations
function validateForm() {
    let isValid = true;
    let errorMessages = [];
    
    // Clear previous errors
    $('.form-control, .form-select').removeClass('error');
    
    // Check required fields with shake animation
    const requiredFields = ['age', 'annual_income', 'monthly_expenses', 'old_dependents', 
                          'young_dependents', 'occupants_count', 'house_area', 
                          'loan_installments', 'type_of_house', 'sex'];
    
    requiredFields.forEach(field => {
        if (!$(`#${field}`).val()) {
            $(`#${field}`).addClass('shake');
            setTimeout(() => {
                $(`#${field}`).removeClass('shake');
            }, 1000);
            errorMessages.push(`Please enter ${field.replace('_', ' ')}`);
            isValid = false;
        }
    });
    
    // Check numeric values with bounce animation
    const numericFields = ['age', 'annual_income', 'monthly_expenses', 'old_dependents', 
                         'young_dependents', 'occupants_count', 'house_area', 
                         'loan_installments'];
    
    numericFields.forEach(field => {
        if ($(`#${field}`).val() && isNaN($(`#${field}`).val())) {
            $(`#${field}`).addClass('bounce');
            setTimeout(() => {
                $(`#${field}`).removeClass('bounce');
            }, 1000);
            errorMessages.push(`${field.replace('_', ' ')} must be a number`);
            isValid = false;
        }
    });
    
    // Show errors with fade animation
    if (!isValid) {
        showError(errorMessages.join('<br>'));
        $('.error').addClass('fade-in');
        setTimeout(() => {
            $('.error').removeClass('fade-in');
        }, 1000);
    }
    
    return isValid;
}

// Show loading state with animation
function showLoading() {
    $('.loading').addClass('fade-in');
    setTimeout(() => {
        $('.loading').removeClass('fade-in');
        $('.result-box').hide();
    }, 500);
}

// Handle successful prediction with animation
function handleSuccess(response) {
    $('.loading').addClass('fade-out');
    setTimeout(() => {
        $('.loading').removeClass('fade-out');
        
        if (response.status === 'success') {
            showSuccessResult(response.prediction);
        } else {
            showError(response.message);
        }
    }, 500);
}

// Show success result with animation
function showSuccessResult(prediction) {
    $('.result-box').addClass('fade-in');
    setTimeout(() => {
        $('.result-box').removeClass('fade-in');
        $('.success').html(`
            <h2>₹ ${prediction.toFixed(2)}</h2>
            <p>Your predicted loan amount is ready!</p>
            <button class="btn btn-primary mt-3" onclick="resetForm()">
                <i class="fas fa-redo me-2"></i>Try Another Prediction
            </button>
        `);
    }, 500);
}

// Show error with animation
function showError(message) {
    $('.result-box').addClass('fade-in');
    setTimeout(() => {
        $('.result-box').removeClass('fade-in');
        $('.error').html(`
            <h4>Error</h4>
            <p>${message}</p>
            <button class="btn btn-warning mt-3" onclick="resetForm()">
                <i class="fas fa-redo me-2"></i>Try Again
            </button>
        `);
    }, 500);
}

// Reset form with animation
function resetForm() {
    $('#loanForm')[0].reset();
    $('.result-box').addClass('fade-out');
    $('.loading').addClass('fade-out');
    setTimeout(() => {
        $('.result-box').removeClass('fade-out');
        $('.loading').removeClass('fade-out');
        $('.result-box').hide();
        $('.loading').hide();
    }, 500);
}

// Add smooth scrolling for anchor links with animation
$('a[href^="#"]').on('click', function(e) {
    e.preventDefault();
    const target = $($(this).attr('href'));
    if (target.length) {
        $('html, body').animate({
            scrollTop: target.offset().top
        }, 1000, 'easeInOutQuart');
    }
});