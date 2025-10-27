<?php
include "../conn.php";

header('Content-Type: application/json');

$response = array();

if (isset($_GET['lang_name'])) {
    $lang_name = mysqli_real_escape_string($conn, $_GET['lang_name']);
    $lang_name = strtolower($lang_name);

    // Query to check if the language exists (case-insensitive)
    $lang_query = "SELECT lang_id FROM languages WHERE LOWER(lang_name) = ?";
    $lang_stmt = $conn->prepare($lang_query);
    if ($lang_stmt === false) {
        $response['status'] = 'error';
        $response['message'] = 'Failed to prepare language query: ' . $conn->error;
        echo json_encode($response, JSON_UNESCAPED_UNICODE);
        exit;
    }
    $lang_stmt->bind_param("s", $lang_name);
    $lang_stmt->execute();
    $lang_result = $lang_stmt->get_result();

    if ($lang_result->num_rows > 0) {
        $lang_row = $lang_result->fetch_assoc();
        $lang_id = $lang_row['lang_id'];

        // Language found, get its phrases
        $phrase_query = "SELECT phrase, translation FROM phrases WHERE lang_id = ?";
        $phrase_stmt = $conn->prepare($phrase_query);
        if ($phrase_stmt === false) {
            $response['status'] = 'error';
            $response['message'] = 'Failed to prepare phrase query: ' . $conn->error;
            echo json_encode($response, JSON_UNESCAPED_UNICODE);
            exit;
        }
        $phrase_stmt->bind_param("i", $lang_id);
        $phrase_stmt->execute();
        $phrase_result = $phrase_stmt->get_result();

        $phrases = array();
        while ($phrase_row = $phrase_result->fetch_assoc()) {
            $phrases[] = array(
                'phrase' => $phrase_row['phrase'],
                'translation' => $phrase_row['translation']
            );
        }
        $response['status'] = 'success';
        $response['phrases'] = $phrases;
    } else {
        $response['status'] = 'error';
        $response['message'] = 'Language not found';
    }
} else {
    $response['status'] = 'error';
    $response['message'] = 'lang_name parameter is missing';
}

echo json_encode($response, JSON_UNESCAPED_UNICODE);
?>