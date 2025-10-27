<?php
// Include database connection
include "../conn.php";

// Query to get all languages
$query = "SELECT * FROM languages";
$result = mysqli_query($conn, $query);

$languages = array();
while ($row = mysqli_fetch_assoc($result)) {
    $languages[] = $row;
}

// Close database connection
mysqli_close($conn);

// Set header to JSON
header('Content-Type: application/json');

// Output the JSON data
echo json_encode($languages);
?>