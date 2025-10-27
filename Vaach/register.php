<?php
// Start session at the very beginning
session_start();

error_reporting(E_ALL);
ini_set('display_errors', 1);

include "conn.php";

if (isset($_POST['register'])) {
    $username = mysqli_real_escape_string($conn, $_POST['username']);
    $password = mysqli_real_escape_string($conn, $_POST['password']);
    $email = mysqli_real_escape_string($conn, $_POST['email']);
    $tags = ",";

    // Check for existing username
    $stmt = $conn->prepare("SELECT username FROM users WHERE username = ?");
    $stmt->bind_param("s", $username);
    $stmt->execute();
    $result = $stmt->get_result();
    if ($result->num_rows > 0) {
        $error = "Username already exists.";
    } else {
        // Secure password hashing
        $hashed_password = password_hash($password, PASSWORD_DEFAULT);

        // Prepared statement for secure registration
        $stmt = $conn->prepare("INSERT INTO users (username, passcode, email, tags) VALUES (?, ?, ?, ?)");
        $stmt->bind_param("ssss", $username, $hashed_password, $email, $tags);
        $stmt->execute();

        $u_id_stmt = $conn->prepare("SELECT user_id, tags FROM users WHERE username = ?");
        $u_id_stmt->bind_param("s", $username);
        $u_id_stmt->execute();
        $u_id_result = $u_id_stmt->get_result();
        $row_uid = $u_id_result->fetch_assoc();

        if ($row_uid) {
            $_SESSION['username'] = $username;
            $_SESSION['user_id'] = $row_uid['user_id'];
            $_SESSION['tags'] = explode(",", $row_uid['tags']);
        }

        header("Location: users.php?intro=true");
        exit;
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Create Account - Vaach</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@3.2.0/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        .hero-gradient {
            background: linear-gradient(135deg, #1a56db 0%, #1e40af 100%);
        }
        .animate-fade-in {
            animation: fadeIn 0.6s ease-out forwards;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .password-strength {
            height: 4px;
            transition: all 0.3s ease;
        }
        .strength-0 { width: 0%; background-color: #ef4444; }
        .strength-1 { width: 25%; background-color: #ef4444; }
        .strength-2 { width: 50%; background-color: #f59e0b; }
        .strength-3 { width: 75%; background-color: #3b82f6; }
        .strength-4 { width: 100%; background-color: #10b981; }
    </style>
</head>
<body class="bg-gray-50 font-sans antialiased">

<?php include "header.php"; ?>
<?php include "navbar.php"; ?>

<main class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8 animate-fade-in">
        <div class="text-center">
            <h2 class="mt-6 text-3xl font-extrabold text-gray-900">Create your account</h2>
            <p class="mt-2 text-sm text-gray-600">Join our community of language enthusiasts</p>
        </div>

        <?php if (isset($error)) : ?>
            <div class="bg-red-50 border-l-4 border-red-400 p-4 mb-6 rounded">
                <div class="flex">
                    <div class="flex-shrink-0">
                        <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                        </svg>
                    </div>
                    <div class="ml-3">
                        <p class="text-sm text-red-700"><?php echo htmlspecialchars($error); ?></p>
                    </div>
                </div>
            </div>
        <?php endif; ?>

        <div class="bg-white py-8 px-6 shadow rounded-lg sm:px-10">
            <form class="mb-0 space-y-6" method="POST" id="registerForm">
                <div class="space-y-4">
                    <div>
                        <label for="username" class="block text-sm font-medium text-gray-700">Username</label>
                        <div class="mt-1 flex rounded-md shadow-sm">
                            <span class="inline-flex items-center px-3 rounded-l-md border border-r-0 border-gray-300 bg-gray-50 text-gray-500 sm:text-sm">
                                <i class="fas fa-user"></i>
                            </span>
                            <input id="username" name="username" type="text" required 
                                   class="flex-1 min-w-0 block w-full px-3 py-2 rounded-none rounded-r-md border border-gray-300 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                   minlength="3"
                                   maxlength="30">
                        </div>
                        <p class="mt-1 text-xs text-gray-500" id="username-availability"></p>
                    </div>

                    <div>
                        <label for="email" class="block text-sm font-medium text-gray-700">Email address</label>
                        <div class="mt-1 flex rounded-md shadow-sm">
                            <span class="inline-flex items-center px-3 rounded-l-md border border-r-0 border-gray-300 bg-gray-50 text-gray-500 sm:text-sm">
                                <i class="fas fa-envelope"></i>
                            </span>
                            <input id="email" name="email" type="email" required 
                                   class="flex-1 min-w-0 block w-full px-3 py-2 rounded-none rounded-r-md border border-gray-300 focus:ring-blue-500 focus:border-blue-500 sm:text-sm">
                        </div>
                    </div>

                    <div>
                        <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
                        <div class="mt-1 flex rounded-md shadow-sm">
                            <span class="inline-flex items-center px-3 rounded-l-md border border-r-0 border-gray-300 bg-gray-50 text-gray-500 sm:text-sm">
                                <i class="fas fa-lock"></i>
                            </span>
                            <input id="password" name="password" type="password" required 
                                   class="flex-1 min-w-0 block w-full px-3 py-2 rounded-none border-t border-b border-gray-300 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                   minlength="8"
                                   oninput="checkPasswordStrength(this.value)">
                            <button type="button" class="inline-flex items-center px-3 rounded-r-md border border-l-0 border-gray-300 bg-gray-50 text-gray-500 hover:bg-gray-100" id="togglePassword">
                                <i class="fas fa-eye"></i>
                            </button>
                        </div>
                        <div class="mt-2">
                            <div class="password-strength strength-0 mb-1 rounded-full" id="password-strength"></div>
                            <p class="text-xs text-gray-500" id="password-strength-text">Password strength: <span>Very Weak</span></p>
                        </div>
                    </div>

                    <div>
                        <label for="confirm_password" class="block text-sm font-medium text-gray-700">Confirm Password</label>
                        <div class="mt-1 flex rounded-md shadow-sm">
                            <span class="inline-flex items-center px-3 rounded-l-md border border-r-0 border-gray-300 bg-gray-50 text-gray-500 sm:text-sm">
                                <i class="fas fa-lock"></i>
                            </span>
                            <input id="confirm_password" name="confirm_password" type="password" required 
                                   class="flex-1 min-w-0 block w-full px-3 py-2 rounded-none rounded-r-md border border-gray-300 focus:ring-blue-500 focus:border-blue-500 sm:text-sm">
                        </div>
                        <p class="mt-1 text-xs text-red-600 hidden" id="password-match-error">Passwords do not match</p>
                    </div>
                </div>

                <!-- Terms and Conditions -->
                <div class="space-y-4">
                    <div class="flex items-start">
                        <div class="flex items-center h-5">
                            <input id="terms" name="terms" type="checkbox" class="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded" required>
                        </div>
                        <div class="ml-3 text-sm">
                            <label for="terms" class="font-medium text-gray-700">I agree to the <a href="terms.php" class="text-blue-600 hover:text-blue-500 hover:underline">Terms of Service</a> and <a href="privacy.php" class="text-blue-600 hover:text-blue-500 hover:underline">Privacy Policy</a></label>
                        </div>
                    </div>
                    
                    <div class="flex items-start">
                        <div class="flex items-center h-5">
                            <input id="guidelines" name="guidelines" type="checkbox" class="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded" required>
                        </div>
                        <div class="ml-3 text-sm">
                            <label for="guidelines" class="font-medium text-gray-700">I agree to follow the <a href="guidelines.php" class="text-blue-600 hover:text-blue-500 hover:underline">Community Guidelines</a></label>
                        </div>
                    </div>
                </div>

                <div>
                    <button type="submit" name="register" class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200">
                        Create Account
                    </button>
                </div>
            </form>

        </div>

        <div class="text-center">
            <p class="text-sm text-gray-600">
                Already have an account?
                <a href="login.php" class="font-medium text-blue-600 hover:text-blue-500">Sign in</a>
            </p>
        </div>
    </div>
</main>

<?php include "footer.php"; ?>

<script>
// Toggle password visibility
const togglePassword = document.querySelector('#togglePassword');
const password = document.querySelector('#password');
const confirmPassword = document.querySelector('#confirm_password');

if (togglePassword) {
    togglePassword.addEventListener('click', function() {
        const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
        password.setAttribute('type', type);
        confirmPassword.setAttribute('type', type);
        this.classList.toggle('fa-eye-slash');
    });
}

// Password strength checker
function checkPasswordStrength(password) {
    let strength = 0;
    const strengthBar = document.getElementById('password-strength');
    const strengthText = document.querySelector('#password-strength-text span');
    
    // Check password length
    if (password.length >= 8) strength++;
    // Check for lowercase letters
    if (password.match(/[a-z]+/)) strength++;
    // Check for uppercase letters
    if (password.match(/[A-Z]+/)) strength++;
    // Check for numbers
    if (password.match(/[0-9]+/)) strength++;
    // Check for special characters
    if (password.match(/[!@#$%^&*(),.?":{}|<>]+/)) strength++;
    
    // Cap strength at 4 for our CSS classes
    strength = Math.min(strength, 4);
    
    // Update the UI
    strengthBar.className = `password-strength strength-${strength} mb-1 rounded-full`;
    
    const strengthLabels = ['Very Weak', 'Weak', 'Fair', 'Strong', 'Very Strong'];
    strengthText.textContent = `Password strength: ${strengthLabels[strength]}`;
    
    // Check if passwords match
    if (confirm_password.value && password !== confirm_password.value) {
        document.getElementById('password-match-error').classList.remove('hidden');
    } else {
        document.getElementById('password-match-error').classList.add('hidden');
    }
}

// Check if passwords match on confirm password field change
if (confirmPassword) {
    confirmPassword.addEventListener('input', function() {
        const password = document.getElementById('password').value;
        const errorElement = document.getElementById('password-match-error');
        
        if (this.value && password !== this.value) {
            errorElement.classList.remove('hidden');
        } else {
            errorElement.classList.add('hidden');
        }
    });
}

// Username availability check
const usernameInput = document.getElementById('username');
if (usernameInput) {
    let timeout = null;
    
    usernameInput.addEventListener('input', function() {
        clearTimeout(timeout);
        const username = this.value.trim();
        const availabilityElement = document.getElementById('username-availability');
        
        if (username.length < 3) {
            availabilityElement.textContent = '';
            return;
        }
        
        // Debounce the API call
        timeout = setTimeout(() => {
            // This would be an AJAX call in a real application
            // For now, we'll just show a message based on length
            if (username.length < 3) {
                availabilityElement.textContent = 'Username too short';
                availabilityElement.className = 'mt-1 text-xs text-red-600';
            } else if (username.length > 20) {
                availabilityElement.textContent = 'Username too long (max 20 characters)';
                availabilityElement.className = 'mt-1 text-xs text-red-600';
            } else {
                availabilityElement.textContent = 'Checking availability...';
                availabilityElement.className = 'mt-1 text-xs text-gray-500';
                
                // Simulate API call
                setTimeout(() => {
                    // In a real app, this would check against the server
                    const takenUsernames = ['admin', 'test', 'user'];
                    const isAvailable = !takenUsernames.includes(username.toLowerCase());
                    
                    if (isAvailable) {
                        availabilityElement.textContent = 'Username is available!';
                        availabilityElement.className = 'mt-1 text-xs text-green-600';
                    } else {
                        availabilityElement.textContent = 'Username is already taken';
                        availabilityElement.className = 'mt-1 text-xs text-red-600';
                    }
                }, 500);
            }
        }, 500);
    });
}
</script>

</body>
</html>
