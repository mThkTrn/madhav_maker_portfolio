<?php
// Start session
session_start();

// Include necessary files
include "conn.php";

// Get language ID from URL or redirect to index.php
$lang_id = $_GET["id"] ?? null;
if (!$lang_id) {
    header("Location: index.php?langid=no");
    exit();
}

// Include header and navbar after we've set up the session
include "header.php";
include "navbar.php";

// Check if user is logged in and has admin privileges
if (!isset($_SESSION["user_id"]) || !isset($_SESSION["tags"])) {
    header("Location: login.php");
    exit();
}

// Check if user is admin for this language
$is_admin = false;
$is_super_admin = in_array("superadmin", $_SESSION["tags"]);

if ($is_super_admin) {
    $is_admin = true;
} else {
    $admin_tag = $lang_id . "_a";
    $super_admin_tag = $lang_id . "_sa";

    if (in_array($admin_tag, $_SESSION["tags"]) || in_array($super_admin_tag, $_SESSION["tags"])) {
        $is_admin = true;
    }
}

if (!$is_admin) {
    header("Location: index.php");
    exit();
}

// Fetch language information
$lang_stmt = $conn->prepare("SELECT * FROM languages WHERE lang_id = ?");
$lang_stmt->bind_param("i", $lang_id);
$lang_stmt->execute();
$lang_result = $lang_stmt->get_result();
$lang_info = $lang_result->fetch_assoc();

if (!$lang_info) {
    header("Location: index.php");
    exit();
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Language Admin Panel - <?php echo htmlspecialchars($lang_info['lang_name']); ?></title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        .form-section {
            background-color: #f9fafb;
            border-radius: 0.5rem;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        .nav-tab {
            @apply px-4 py-2 text-sm font-medium rounded-md transition-colors duration-150;
        }
        .nav-tab.active {
            @apply bg-white text-blue-600 shadow-sm;
        }
        .nav-tab:not(.active) {
            @apply text-gray-600 hover:bg-gray-100;
        }
    </style>
</head>
<body class="bg-gray-50 font-sans antialiased">
<?php
// Handle phrase approval or denial actions

// Handle bulk actions
if (isset($_POST['bulk_action'])) {
    $action = $_POST['bulk_action'];
    $section = $_POST['section'];
    
    if ($section === 'changes') {
        $query = "SELECT * FROM phrases WHERE lang_id = $lang_id AND approved = 0 AND replacing != -1";
    } else {
        $query = "SELECT * FROM phrases WHERE lang_id = $lang_id AND approved = 0 AND replacing = -1";
    }
    
    $result = mysqli_query($conn, $query);
    
    while ($row = mysqli_fetch_assoc($result)) {
        // print_r($row);
        $phrase_id = $row['phrase_id'];
        $phrase_user_id = $row['user_id'];
        $phrase_text = $row['phrase'];
        
        if ($action === 'approve') {
            if ($section === 'changes') {
                $old_phrase_id = $row['replacing'];
                $update_query = $conn->prepare("UPDATE phrases SET approved = 1 WHERE phrase_id = ?");
                $update_query->bind_param("i", $phrase_id);
                $update_query->execute();
                addNotif($phrase_user_id, "Your edit to phrase '$phrase_text' was accepted.", "success");
                $expiration_query = "DELETE FROM phrases WHERE phrase_id = $old_phrase_id";
                mysqli_query($conn, $expiration_query);
            } else {
                $update_query = $conn->prepare("UPDATE phrases SET approved = 1 WHERE phrase_id = ?");
                $update_query->bind_param("i", $phrase_id);
                $update_query->execute();
                addNotif($phrase_user_id, "Your submission of phrase '$phrase_text' was accepted.", "success");

                // Check for admin promotion

                if ($phrase_user_id){
                // echo "Phrase User ID: " . htmlspecialchars($phrase_user_id) . "<br>";


                $is_admin_query = "SELECT tags FROM users WHERE user_id = $phrase_user_id";
                $is_admin_query_result = mysqli_query($conn, $is_admin_query);
                
                if (!$is_admin_query_result) {
                    die("Query failed: " . mysqli_error($conn));
                }
                
                $is_admin_tags = explode(",", mysqli_fetch_assoc($is_admin_query_result)["tags"]);
                

                $admin_tag = $lang_id."_a,";
                if (!in_array($admin_tag, $is_admin_tags) && !in_array($lang_id."_sa,", $is_admin_tags)) {
                    $approved_phrases_query = "SELECT COUNT(*) AS count FROM phrases WHERE user_id = $phrase_user_id AND lang_id = $lang_id AND approved = 1";
                    $approved_phrases_result = mysqli_query($conn, $approved_phrases_query);
                    $approved_phrases_row = mysqli_fetch_assoc($approved_phrases_result);
                    $approved_phrases_count = $approved_phrases_row['count'];

                    if ($approved_phrases_count >= 5) {
                        $add_admin_sql = "UPDATE users SET tags = CONCAT(tags, '$admin_tag') WHERE user_id = $phrase_user_id";
                        mysqli_query($conn, $add_admin_sql);
                        addNotif($phrase_user_id, "Congratulations! You are now an admin of language ".$lang_info["lang_name"], "success");
                    }
                }
                }
            }
        } else if ($action === 'deny') {
            $update_query = "DELETE FROM phrases WHERE phrase_id = $phrase_id";
            mysqli_query($conn, $update_query);
            addNotif($phrase_user_id, "Your " . ($section === 'changes' ? "edit to" : "submission of") . " phrase '$phrase_text' was denied.", "failure");
        }
    }
    
    echo '<div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-4" role="alert">
            <strong class="font-bold">Success!</strong>
            <span class="block sm:inline">Bulk action completed successfully!</span>
          </div>';
}


if (isset($_GET['action'])) {
    $phrase_id = $_GET['phrase_id'];
    $stmt = $conn->prepare("SELECT user_id, phrase FROM phrases WHERE phrase_id = ?");
    $stmt->bind_param("i", $phrase_id);
    $stmt->execute();
    $phrase_user_id_result = $stmt->get_result();
    $stmt->close();

    $phrase_user_id_row = mysqli_fetch_assoc($phrase_user_id_result);
    $phrase_user_id = $phrase_user_id_row['user_id'];
    $phrase_text = $phrase_user_id_row["phrase"];

    if ($_GET['action'] == 'approvechange') {
        $update_query = $conn->prepare("UPDATE phrases SET approved = 1 WHERE phrase_id = ?");
        $update_query->bind_param("i", $phrase_id);
        $update_query->execute();
        echo '<div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-4" role="alert">
                <strong class="font-bold">Success!</strong>
                <span class="block sm:inline">Change approved successfully!</span>
              </div>';
        addNotif($phrase_user_id, "Your edit to phrase '$phrase_text' was accepted.", "success");
        $expired_phrase_id = $_GET["oldphrase"];
        $expiration_query = "DELETE FROM phrases WHERE phrase_id = $expired_phrase_id";
        mysqli_query($conn, $expiration_query);
    }
    if ($_GET["action"] == 'denychange') {
        $update_query = "DELETE FROM phrases WHERE phrase_id = $phrase_id";
        mysqli_query($conn, $update_query);
        addNotif($phrase_user_id, "Your edit to phrase '$phrase_text' was denied.", "failure");
        echo '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
                <strong class="font-bold">Error!</strong>
                <span class="block sm:inline">Change denied successfully!</span>
              </div>';
    }
    if ($_GET['action'] == 'approve') {
        $update_query = $conn->prepare("UPDATE phrases SET approved = 1 WHERE phrase_id = ?");
        $update_query->bind_param("i", $phrase_id);
        $update_query->execute();
        echo '<div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-4" role="alert">
                <strong class="font-bold">Success!</strong>
                <span class="block sm:inline">Phrase approved successfully!</span>
              </div>';
        addNotif($phrase_user_id, "Your submission of phrase '$phrase_text' was accepted.", "success");

        // Check if user is an admin
        $is_admin_query = "SELECT tags FROM users WHERE user_id = $phrase_user_id";
        $is_admin_query_result = mysqli_query($conn, $is_admin_query);
        $is_admin_tags = explode(",", mysqli_fetch_assoc($is_admin_query_result)["tags"]);

        $admin_tag = $lang_id."_a,";
        if (!in_array($admin_tag, $is_admin_tags) && !in_array($lang_id."_sa,", $is_admin_tags)) {
            // Adding admin permission to users with more than 5 approved posts
            $approved_phrases_query = "SELECT COUNT(*) AS count FROM phrases WHERE user_id = $phrase_user_id AND lang_id = $lang_id AND approved = 1";
            $approved_phrases_result = mysqli_query($conn, $approved_phrases_query);
            $approved_phrases_row = mysqli_fetch_assoc($approved_phrases_result);
            $approved_phrases_count = $approved_phrases_row['count'];

            if ($approved_phrases_count >= 5) {
                $add_admin_sql = "UPDATE users SET tags = CONCAT(tags, '$admin_tag') WHERE user_id = $phrase_user_id";
                mysqli_query($conn, $add_admin_sql);
                addNotif($phrase_user_id, "Congratulations! You are now an admin of language ".$lang_info["lang_name"], "success");
            }
        }
    } elseif ($_GET['action'] == 'deny') {
        $update_query = "DELETE FROM phrases WHERE phrase_id = $phrase_id";
        mysqli_query($conn, $update_query);
        addNotif($phrase_user_id, "Your submission of phrase '$phrase_text' was denied.", "failure");
        echo '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
                <strong class="font-bold">Error!</strong>
                <span class="block sm:inline">Phrase denied successfully!</span>
              </div>';
    }
}

// Add this after the existing approval handling code

// Handle CSV upload
if (isset($_FILES['phrase_csv']) && isset($_POST['upload_csv'])) {
    $file = $_FILES['phrase_csv'];
    if ($file['error'] == 0 && ($file['type'] == 'text/csv' || $file['type'] == 'application/vnd.ms-excel')) {
        $handle = fopen($file['tmp_name'], "r");
        
        // Get headers and normalize them
        $headers = fgetcsv($handle);
        $normalized_headers = array();
        $valid_fields = array('phrase', 'romanization', 'translation', 'speech_part', 'phonetic', 'ipa');
        
        foreach ($headers as $index => $header) {
            $header = strtolower(trim($header));
            foreach ($valid_fields as $field) {
                if (strpos($header, $field) !== false) {
                    $normalized_headers[$index] = $field;
                    break;
                }
            }
        }
        
        // Process each row
        $success_count = 0;
        $error_count = 0;
        
        while (($data = fgetcsv($handle)) !== FALSE) {
            $phrase_data = array_fill_keys($valid_fields, ''); // Initialize with empty values
            
            // Map CSV data to fields
            foreach ($normalized_headers as $index => $field) {
                if (isset($data[$index])) {
                    $phrase_data[$field] = $data[$index];
                }
            }
            
            // Skip if required fields are empty
            if (empty($phrase_data['phrase']) || empty($phrase_data['translation'])) {
                $error_count++;
                continue;
            }
            
            // Insert into database
            $stmt = $conn->prepare("INSERT INTO phrases (lang_id, phrase, romanization, translation, speech_part, phonetic, ipa, approved, replacing) VALUES (?, ?, ?, ?, ?, ?, ?, 0, -1)");
            $stmt->bind_param("issssss", 
                $lang_id,
                $phrase_data['phrase'],
                $phrase_data['romanization'],
                $phrase_data['translation'],
                $phrase_data['speech_part'],
                $phrase_data['phonetic'],
                $phrase_data['ipa']
            );
            
            if ($stmt->execute()) {
                $success_count++;
            } else {
                $error_count++;
            }
            $stmt->close();
        }
        fclose($handle);
        
        echo "<div class='bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-4' role='alert'>
                <strong class='font-bold'>Upload Complete!</strong>
                <span class='block sm:inline'>Successfully added $success_count phrases. Failed to add $error_count phrases.</span>
              </div>";
    } else {
        echo "<div class='bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4' role='alert'>
                <strong class='font-bold'>Error!</strong>
                <span class='block sm:inline'>Please upload a valid CSV file.</span>
              </div>";
    }
}

$username = $_SESSION['username'];
$tags = $_SESSION['tags'];
if (!in_array($lang_id . '_a', $tags) && !in_array($lang_id . '_sa', $tags)) {
    header("Location: language.php?id=$lang_id");  // Redirect non-admins to language page
    exit;
}

// Fetch phrases for approval
$pending_phrases_query = "SELECT * FROM phrases WHERE lang_id = $lang_id AND approved = 0 AND replacing = -1";
$pending_phrases_result = mysqli_query($conn, $pending_phrases_query);

$changing_phrases_query = "SELECT * FROM phrases WHERE lang_id = $lang_id AND approved = 0 AND replacing != -1";
$changing_phrases_result = mysqli_query($conn, $changing_phrases_query);
?>

<main class="bg-white min-h-screen">
    <div class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <!-- Back button -->
        <!-- <div class="mb-6">
            <a href="language.php?id=<?php echo $lang_id; ?>" class="text-blue-600 hover:text-blue-800 flex items-center">
                <i class="fas fa-arrow-left mr-2"></i> Back to <?php echo htmlspecialchars($lang_info['lang_name']); ?>
            </a>
        </div> -->
        
        <!-- Header -->
        <div class="mb-8">
            <h1 class="text-3xl font-bold text-gray-900">Admin Panel: <?php echo htmlspecialchars($lang_info['lang_name']); ?></h1>
            <p class="mt-2 text-sm text-gray-600">Manage phrases, changes, and settings for <?php echo htmlspecialchars($lang_info['lang_name']); ?>.</p>
        </div>
        
        <!-- Language Info Card -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <h2 class="text-lg font-medium text-gray-900 mb-4">Language Information</h2>
                    <div class="space-y-2">
                        <p class="text-gray-700">
                            <span class="font-medium">Location:</span> 
                            <?php echo strlen($lang_info["lang_place"]) == 0 ? "Not specified" : htmlspecialchars($lang_info['lang_place']); ?>
                        </p>
                        <p class="text-gray-700">
                            <span class="font-medium">Vitality:</span> 
                            <?php echo str_replace("_", " ", ucfirst($lang_info['lang_vitality'])); ?>
                        </p>
                    </div>
                </div>
                
                <div class="space-y-4">
                    <div class="flex flex-wrap gap-3">
                        <?php if (isset($_SESSION["user_id"])): ?>
                            <a href="phrase_request.php?id=<?php echo htmlspecialchars($lang_id); ?>" 
                               class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                                <i class="fas fa-plus-circle mr-2"></i> Suggest a Phrase
                            </a>
                        <?php else: ?>
                            <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 w-full">
                                <div class="flex">
                                    <div class="flex-shrink-0">
                                        <i class="fas fa-exclamation-triangle text-yellow-400"></i>
                                    </div>
                                    <div class="ml-3">
                                        <p class="text-sm text-yellow-700">
                                            <a href="login.php" class="font-medium text-yellow-700 hover:text-yellow-600 underline">Log in</a> to suggest or edit phrases.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        <?php endif; ?>
                        
                        <a href="language.php?id=<?php echo htmlspecialchars($lang_id); ?>" 
                           class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                            <i class="fas fa-language mr-2"></i> View Language Page
                        </a>
                    </div>
                    
                    <!-- CSV Upload Section -->
                    <div class="mt-4">
                        <h3 class="text-sm font-medium text-gray-700 mb-2">Bulk Import</h3>
                        <form action="" method="post" enctype="multipart/form-data" class="flex items-center space-x-2">
                            <div class="flex-1">
                                <input type="file" name="phrase_csv" accept=".csv" required 
                                       class="block w-full text-sm text-gray-500
                                              file:mr-4 file:py-2 file:px-4
                                              file:rounded-md file:border-0
                                              file:text-sm file:font-medium
                                              file:bg-blue-50 file:text-blue-700
                                              hover:file:bg-blue-100">
                            </div>
                            <button type="submit" name="upload_csv" 
                                    class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500">
                                <i class="fas fa-file-import mr-2"></i> Import CSV
                            </button>
                            <div class="relative">
                                <button type="button" class="text-gray-400 hover:text-gray-500">
                                    <i class="fas fa-question-circle text-xl"></i>
                                </button>
                                <div class="hidden absolute z-10 w-64 p-3 bg-white border border-gray-200 rounded-lg shadow-lg -left-32 bottom-full mb-2">
                                    <h4 class="font-medium text-gray-900 mb-2">CSV Format Guidelines:</h4>
                    <ul class="list-disc pl-4 mt-1">
                        <li>Accepts columns containing these keywords: phrase, romanization, translation, part of speech, phonetic, ipa</li>
                        <li>Column names are case-insensitive</li>
                        <li>Matches partial names (e.g., "Phrase (Angika)" matches "phrase")</li>
                        <li>Only phrase and translation are required</li>
                        <li>Extra columns are ignored</li>
                                    </ul>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Pending Changes & Additions Section -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden mb-8">
            <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
                <h2 class="text-lg font-medium text-gray-900">
                    <i class="fas fa-tasks mr-2 text-blue-500"></i> Pending Review
                </h2>
                <p class="mt-1 text-sm text-gray-500">Review and manage all pending changes and additions.</p>
            </div>
            
            <!-- Section for Existing Phrase Changes -->
            <div class="px-6 pt-4 pb-2 border-b border-gray-100">
                <h3 class="text-md font-medium text-gray-800 flex items-center">
                    <i class="fas fa-exchange-alt mr-2 text-blue-400"></i> Changes to Existing Phrases
                </h3>
            </div>
            
            <div class="p-6">
                <div class="mb-6 flex space-x-3">
                    <form method="post" class="inline">
                        <input type="hidden" name="section" value="changes">
                        <button type="submit" name="bulk_action" value="approve" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500">
                            <i class="fas fa-check-circle mr-2"></i> Approve All
                        </button>
                    </form>
                    <form method="post" class="inline">
                        <input type="hidden" name="section" value="changes">
                        <button type="submit" name="bulk_action" value="deny" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500">
                            <i class="fas fa-times-circle mr-2"></i> Deny All
                        </button>
                    </form>
                </div>

            <?php if (mysqli_num_rows($changing_phrases_result) > 0): ?>
                <table class="min-w-full bg-white border border-gray-300 rounded-lg">
                    <thead class="bg-gray-200">
                        <tr>
                            <th class="py-2 px-4 border-b text-left text-gray-600">Phrase</th>
                            <th class="py-2 px-4 border-b text-left text-gray-600">Romanization</th>
                            <th class="py-2 px-4 border-b text-left text-gray-600">Part of Speech</th>
                            <th class="py-2 px-4 border-b text-left text-gray-600">Translation</th>
                            <th class="py-2 px-4 border-b text-left text-gray-600">Phonetic</th>
                            <th class="py-2 px-4 border-b text-left text-gray-600">IPA</th>
                            <th class="py-2 px-4 border-b text-left text-gray-600">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php while ($row = mysqli_fetch_assoc($changing_phrases_result)): ?>
                            <?php
                            $old_phrase_id = $row["replacing"];
                            $old_phrase_query = "SELECT * FROM phrases WHERE phrase_id = $old_phrase_id";
                            $old_phrase_result = mysqli_query($conn, $old_phrase_query);
                            ?>
                            <?php while ($oldrow = mysqli_fetch_assoc($old_phrase_result)): ?>
                                <tr>
                                    <td class="py-2 px-4 border-b"><?php echo htmlspecialchars($oldrow['phrase']); ?></td>
                                    <td class="py-2 px-4 border-b"><?php echo htmlspecialchars($oldrow['romanization']); ?></td>
                                    <td class="py-2 px-4 border-b"><?php echo htmlspecialchars($oldrow['speech_part']); ?></td>
                                    <td class="py-2 px-4 border-b"><?php echo htmlspecialchars($oldrow['translation']); ?></td>
                                    <td class="py-2 px-4 border-b"><?php echo htmlspecialchars($oldrow['phonetic']); ?></td>
                                    <td class="py-2 px-4 border-b"><?php echo htmlspecialchars($oldrow['ipa']); ?></td>
                                    <td class="py-2 px-4 border-b"></td>
                                </tr>
                                <tr>
                                    <td class="py-2 px-4 border-b"><?php echo htmlspecialchars($row['phrase']); ?></td>
                                    <td class="py-2 px-4 border-b"><?php echo htmlspecialchars($row['romanization']); ?></td>
                                    <td class="py-2 px-4 border-b"><?php echo htmlspecialchars($row['speech_part']); ?></td>
                                    <td class="py-2 px-4 border-b"><?php echo htmlspecialchars($row['translation']); ?></td>
                                    <td class="py-2 px-4 border-b"><?php echo htmlspecialchars($row['phonetic']); ?></td>
                                    <td class="py-2 px-4 border-b"><?php echo htmlspecialchars($row['ipa']); ?></td>
                                    <td class="py-2 px-4 border-b">
                                        <a href="language_admin.php?id=<?php echo htmlspecialchars($lang_id); ?>&action=approvechange&phrase_id=<?php echo htmlspecialchars($row['phrase_id']); ?>&oldphrase=<?php echo htmlspecialchars($old_phrase_id); ?>" class="bg-green-500 text-white py-1 px-2 rounded hover:bg-green-600">Approve</a>
                                        <br><br>
                                        <a href="language_admin.php?id=<?php echo htmlspecialchars($lang_id); ?>&action=denychange&phrase_id=<?php echo htmlspecialchars($row['phrase_id']); ?>" class="bg-red-500 text-white py-1 px-2 rounded hover:bg-red-600">Deny</a>
                                    </td>
                                </tr>
                            <?php endwhile; ?>
                        <?php endwhile; ?>
                    </tbody>
                </table>
            <?php else: ?>
                <div class="p-6">
                    <p class="text-gray-500 text-center py-4">No items to review.</p>
                </div>
            <?php endif; ?>

            <!-- Section for New Phrase Additions -->
            <div class="px-6 pt-6 pb-2 border-t border-gray-100">
                <h3 class="text-md font-medium text-gray-800 flex items-center">
                    <i class="fas fa-plus-circle mr-2 text-green-500"></i> New Phrase Submissions
                </h3>
            </div>

            <div class="mb-6 flex space-x-3">
                <form method="post" class="inline">
                    <input type="hidden" name="section" value="additions">
                    <button type="submit" name="bulk_action" value="approve" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500">
                        <i class="fas fa-check-circle mr-2"></i> Approve All
                    </button>
                </form>
                <form method="post" class="inline">
                    <input type="hidden" name="section" value="additions">
                    <button type="submit" name="bulk_action" value="deny" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500">
                        <i class="fas fa-times-circle mr-2"></i> Deny All
                    </button>
                </form>
            </div>

            <?php if (mysqli_num_rows($pending_phrases_result) > 0): ?>
                <table class="min-w-full bg-white border border-gray-300 rounded-lg">
                    <thead class="bg-gray-200">
                        <tr>
                            <th class="py-2 px-4 border-b text-left text-gray-600">Phrase</th>
                            <th class="py-2 px-4 border-b text-left text-gray-600">Romanization</th>
                            <th class="py-2 px-4 border-b text-left text-gray-600">Part of Speech</th>
                            <th class="py-2 px-4 border-b text-left text-gray-600">Translation</th>
                            <th class="py-2 px-4 border-b text-left text-gray-600">Phonetic</th>
                            <th class="py-2 px-4 border-b text-left text-gray-600">IPA</th>
                            <th class="py-2 px-4 border-b text-left text-gray-600">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php while ($row = mysqli_fetch_assoc($pending_phrases_result)): ?>
                            <tr>
                                <td class="py-2 px-4 border-b"><?php echo htmlspecialchars($row['phrase']); ?></td>
                                <td class="py-2 px-4 border-b"><?php echo htmlspecialchars($row['romanization']); ?></td>
                                <td class="py-2 px-4 border-b"><?php echo htmlspecialchars($row['speech_part']); ?></td>
                                <td class="py-2 px-4 border-b"><?php echo htmlspecialchars($row['translation']); ?></td>
                                <td class="py-2 px-4 border-b"><?php echo htmlspecialchars($row['phonetic']); ?></td>
                                <td class="py-2 px-4 border-b"><?php echo htmlspecialchars($row['ipa']); ?></td>
                                <td class="py-2 px-4 border-b">
                                    <a href="language_admin.php?id=<?php echo htmlspecialchars($lang_id); ?>&action=approve&phrase_id=<?php echo htmlspecialchars($row['phrase_id']); ?>" class="bg-green-500 text-white py-1 px-2 rounded hover:bg-green-600">Approve</a>
                                    <a href="language_admin.php?id=<?php echo htmlspecialchars($lang_id); ?>&action=deny&phrase_id=<?php echo htmlspecialchars($row['phrase_id']); ?>" class="bg-red-500 text-white py-1 px-2 rounded hover:bg-red-600">Deny</a>
                                </td>
                            </tr>
                        <?php endwhile; ?>
                    </tbody>
                </table>
            <?php else: ?>
                <div class="p-6">
                    <p class="text-gray-500 text-center py-4">No items to review.</p>
                </div>
            <?php endif; ?>
        </div>
    </div>
</main>

<?php include "footer.php"; ?>
<?php mysqli_close($conn); ?>

<script>
// Tab switching functionality
const tabs = document.querySelectorAll('.nav-tab');
const sections = document.querySelectorAll('div[id^="tab-"]');

tabs.forEach(tab => {
    tab.addEventListener('click', (e) => {
        e.preventDefault();
        const targetId = tab.getAttribute('href').substring(1);
        
        // Update active tab
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        
        // Show target section
        document.querySelectorAll('.tab-content').forEach(section => {
            section.classList.add('hidden');
        });
        document.getElementById(targetId).classList.remove('hidden');
    });
});

// Initialize first tab as active
if (tabs.length > 0) {
    tabs[0].click();
}
</script>

</body>
</html>