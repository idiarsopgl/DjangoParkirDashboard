<?php
/**
 * Example PHP file that uses the Django bridge
 */

// Include the PHP bridge
require_once 'php_bridge.php';

// Set content type to HTML
header('Content-Type: text/html; charset=UTF-8');
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Parking System PHP Interface</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
        }
        h1 {
            color: #0066cc;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .card {
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        table, th, td {
            border: 1px solid #ddd;
        }
        th, td {
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        .btn {
            display: inline-block;
            background-color: #0066cc;
            color: white;
            padding: 8px 16px;
            text-decoration: none;
            border-radius: 4px;
            border: none;
            cursor: pointer;
        }
        .btn:hover {
            background-color: #0052a3;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Parking System - PHP Frontend</h1>
        
        <div class="card">
            <h2>Current Parking Records</h2>
            <?php
            // Get parking records from Django
            $records = get_parking_records();
            
            if ($records['status'] === 200) {
                $data = json_decode($records['data'], true);
                
                if (!empty($data)) {
                    echo '<table>';
                    echo '<tr>
                            <th>Plate Number</th>
                            <th>Vehicle Type</th>
                            <th>Entry Time</th>
                            <th>Exit Time</th>
                            <th>Fee</th>
                            <th>Status</th>
                          </tr>';
                    
                    foreach ($data as $record) {
                        echo '<tr>';
                        echo '<td>' . htmlspecialchars($record['vehicle']['plate_number']) . '</td>';
                        echo '<td>' . htmlspecialchars($record['vehicle']['vehicle_type']) . '</td>';
                        echo '<td>' . htmlspecialchars($record['entry_time']) . '</td>';
                        echo '<td>' . (isset($record['exit_time']) ? htmlspecialchars($record['exit_time']) : 'N/A') . '</td>';
                        echo '<td>' . (isset($record['fee']) ? 'Rp ' . number_format($record['fee'], 0, ',', '.') : 'N/A') . '</td>';
                        echo '<td>' . ($record['is_paid'] ? 'Paid' : 'Unpaid') . '</td>';
                        echo '</tr>';
                    }
                    
                    echo '</table>';
                } else {
                    echo '<p>No parking records found.</p>';
                }
            } else {
                echo '<p>Error retrieving data from Django backend. Status: ' . $records['status'] . '</p>';
            }
            ?>
        </div>
        
        <div class="card">
            <h2>New Vehicle Entry</h2>
            <form method="post" action="process_entry.php">
                <div style="margin-bottom: 15px;">
                    <label for="plate_number">Plate Number:</label>
                    <input type="text" id="plate_number" name="plate_number" required style="padding: 8px; width: 100%; max-width: 300px;">
                </div>
                
                <div style="margin-bottom: 15px;">
                    <label for="vehicle_type">Vehicle Type:</label>
                    <select id="vehicle_type" name="vehicle_type" required style="padding: 8px; width: 100%; max-width: 300px;">
                        <option value="CAR">Car</option>
                        <option value="MOTORCYCLE">Motorcycle</option>
                        <option value="TRUCK">Truck</option>
                    </select>
                </div>
                
                <div style="margin-bottom: 15px;">
                    <label for="color">Vehicle Color:</label>
                    <input type="text" id="color" name="color" required style="padding: 8px; width: 100%; max-width: 300px;">
                </div>
                
                <button type="submit" class="btn">Register Entry</button>
            </form>
        </div>
    </div>
</body>
</html> 