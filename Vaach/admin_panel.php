<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 font-sans">

<?php
include "header.php";
include "navbar.php";
include "conn.php";

if (!in_array("superadmin", $_SESSION["tags"]) && !in_array("admin", $_SESSION["tags"])) {
  header("Location: index.php");
  exit;
}

// Check for language approval action
if (isset($_GET['approve'])) {
  $lang_id = $_GET['approve'];
  $stmt = $conn->prepare("UPDATE languages SET approved = 1 WHERE lang_id = ?");
  $stmt->bind_param("i", $lang_id);
  $stmt->execute();
  $success = "Language approved successfully!";

  $user_id = $_GET['u'];
  $stmt = $conn->prepare("UPDATE users SET tags = CONCAT(tags, '".$lang_id."_sa,') WHERE user_id = ".$user_id."");
  $stmt->execute();
  $success = "Language approved successfully!";
}

if (isset($_GET['delete'])) {
  $lang_id = $_GET['delete'];
  $stmt = $conn->prepare("DELETE from languages WHERE lang_id = ?");
  $stmt->bind_param("i", $lang_id);
  $stmt->execute();
  $success = "Language deleted successfully!";
}

// Fetch unapproved languages
$query = "SELECT * FROM languages WHERE approved = 0";
$result = mysqli_query($conn, $query);
?>

<div class="min-h-screen flex flex-col">
    <main class="flex-grow p-6">
        <?php if (isset($success)): ?>
            <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-4" role="alert">
                <strong class="font-bold">Success!</strong>
                <span class="block sm:inline"><?php echo $success; ?></span>
            </div>
        <?php endif; ?>

        <div class="container mx-auto bg-white p-6 rounded-lg shadow-md">
            <h2 class="text-3xl font-bold text-gray-900 mb-6">Admin Panel</h2>
            <h3 class="text-2xl font-semibold text-gray-800 mb-4">Unapproved Languages</h3>
            <?php if (mysqli_num_rows($result) > 0): ?>
                <div class="overflow-x-auto">
                    <table class="min-w-full bg-white border border-gray-300 rounded-lg">
                        <thead class="bg-gray-200">
                            <tr>
                                <th class="py-2 px-4 border-b text-left text-gray-600">#</th>
                                <th class="py-2 px-4 border-b text-left text-gray-600">Language Name</th>
                                <th class="py-2 px-4 border-b text-left text-gray-600">Location</th>
                                <th class="py-2 px-4 border-b text-left text-gray-600">Information</th>
                                <th class="py-2 px-4 border-b text-left text-gray-600">Submitted by</th>
                                <th class="py-2 px-4 border-b text-left text-gray-600">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php while ($row = mysqli_fetch_assoc($result)): ?>
                                <tr class="border-b hover:bg-gray-50">
                                    <td class="py-2 px-4"><?php echo $row['lang_id']; ?></td>
                                    <td class="py-2 px-4"><?php echo $row['lang_name']; ?></td>
                                    <td class="py-2 px-4"><?php echo $row['lang_place']; ?></td>
                                    <td class="py-2 px-4"><?php echo $row['lang_info']; ?></td>
                                    <td class="py-2 px-4"><?php echo $row["user_id"]; ?></td>
                                    <td class="py-2 px-4">
                                        <a href="admin_panel.php?approve=<?php echo $row['lang_id']; ?>&u=<?php echo $row["user_id"] ?>" class="text-blue-600 hover:text-blue-800 mr-2">Approve</a>
                                        <a href="admin_panel.php?delete=<?php echo $row['lang_id']; ?>" class="text-red-600 hover:text-red-800" onclick="return confirm('Are you sure you want to delete this language request?');">Delete</a>
                                    </td>
                                </tr>
                            <?php endwhile; ?>
                        </tbody>
                    </table>
                </div>
            <?php else: ?>
                <p class="text-gray-600">There are currently no unapproved language requests.</p>
            <?php endif; ?>
        </div>
    </main>

    <?php include "footer.php"; ?>
</div>

</body>
</html>
