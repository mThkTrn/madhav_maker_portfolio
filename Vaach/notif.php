<?php
include "header.php";
include "conn.php";
include "navbar.php";

session_start();

// Ensure user is logged in
if (!isset($_SESSION['username'])) {
    header("Location: login.php");
    exit;
}

// Get username from session
$username = $_SESSION['username'];

// Fetch user information
$user_query = "SELECT * FROM users WHERE username = '$username'";
$user_result = mysqli_query($conn, $user_query);
$user = mysqli_fetch_assoc($user_result);

// Fetch notifications for the user
$notifications_query = "SELECT * FROM notifications WHERE user_id = " . $user['user_id'];
$notifications_result = mysqli_query($conn, $notifications_query);
?>

<div class="container mx-auto p-4 bg-white shadow-md rounded-lg mt-6">
    <h2 class="text-2xl font-bold mb-4">Welcome, <?php echo htmlspecialchars($user['username']); ?>!</h2>

    <div class="bg-gray-100 p-4 rounded-lg mb-6">
        <h3 class="text-xl font-semibold mb-2">User Information</h3>
        <ul class="space-y-2">
            <li class="bg-white p-3 rounded-lg shadow-sm"><strong class="font-medium">Username:</strong> <?php echo htmlspecialchars($user['username']); ?></li>
            <li class="bg-white p-3 rounded-lg shadow-sm"><strong class="font-medium">Tags:</strong> <?php echo htmlspecialchars($user['tags']); ?></li>
        </ul>
    </div>

    <div>
        <h3 class="text-xl font-semibold mb-2">Notifications</h3>

        <?php if (mysqli_num_rows($notifications_result) > 0): ?>
            <ul class="space-y-2">
                <?php while ($notification = mysqli_fetch_assoc($notifications_result)): ?>
                    <li class="bg-white p-3 rounded-lg shadow-sm">
                        <?php echo htmlspecialchars($notification['notif_text']); ?>
                        <span class="float-right text-sm text-gray-500">(Type: <?php echo htmlspecialchars($notification['notif_type']); ?>)</span>
                    </li>
                <?php endwhile; ?>
            </ul>
        <?php else: ?>
            <p class="text-gray-500">You currently have no notifications.</p>
        <?php endif; ?>
    </div>
</div>

<?php require_once("footer.php"); ?>

<?php mysqli_close($conn); ?>
