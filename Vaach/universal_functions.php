<?php

include "conn.php";

function addNotif($notif_uid, $notif_text, $notif_type){
    global $conn;

    $stmt = $conn->prepare("INSERT INTO notifications (user_id, notif_text, notif_type) VALUES (?, ?, ?)");
    $stmt->bind_param("iss", $notif_uid, $notif_text, $notif_type);
    $stmt->execute();
}