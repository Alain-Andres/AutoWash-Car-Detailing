-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 10, 2025 at 06:30 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `car_detailing_db`
--
CREATE DATABASE IF NOT EXISTS `car_detailing_db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `car_detailing_db`;

-- --------------------------------------------------------

--
-- Table structure for table `appointments`
--

CREATE TABLE `appointments` (
  `id` int(11) NOT NULL,
  `customer_id` int(11) NOT NULL,
  `vehicle_id` int(11) NOT NULL,
  `service_id` int(11) NOT NULL,
  `appointment_date` datetime NOT NULL,
  `notes` text DEFAULT NULL,
  `status` enum('scheduled','in-progress','completed','cancelled') DEFAULT 'scheduled',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `appointments`
--

INSERT INTO `appointments` (`id`, `customer_id`, `vehicle_id`, `service_id`, `appointment_date`, `notes`, `status`, `created_at`, `updated_at`) VALUES
(1, 1, 1, 1, '2025-05-09 23:06:38', 'First time customer', 'completed', '2025-05-08 15:06:38', '2025-05-08 15:18:20'),
(2, 2, 3, 3, '2025-05-10 23:06:38', 'Customer requested special attention to leather seats', 'scheduled', '2025-05-08 15:06:38', '2025-05-08 15:06:38'),
(3, 3, 4, 2, '2025-05-07 23:06:38', 'Completed service', 'completed', '2025-05-08 15:06:38', '2025-05-08 15:06:38'),
(4, 3, 4, 5, '2025-05-09 11:30:00', '', 'scheduled', '2025-05-08 15:26:07', '2025-05-08 15:26:07'),
(6, 1, 1, 5, '2025-05-08 10:00:00', 'Please', 'scheduled', '2025-05-08 15:31:02', '2025-05-08 15:31:02');

-- --------------------------------------------------------

--
-- Table structure for table `customers`
--

CREATE TABLE `customers` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `phone` varchar(20) NOT NULL,
  `address` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `customers`
--

INSERT INTO `customers` (`id`, `name`, `email`, `phone`, `address`, `created_at`, `updated_at`) VALUES
(1, 'John Smith', 'john@example.com', '555-123-4567', '123 Main St, Anytown, CA 90210', '2025-05-08 15:06:38', '2025-05-08 15:06:38'),
(2, 'Jane Doe', 'jane@example.com', '555-987-6543', '456 Oak Ave, Somewhere, CA 90211', '2025-05-08 15:06:38', '2025-05-08 15:06:38'),
(3, 'Bob Johnson', 'bob@example.com', '555-555-5555', '789 Elm St, Nowhere, CA 90212', '2025-05-08 15:06:38', '2025-05-08 15:06:38');

-- --------------------------------------------------------

--
-- Table structure for table `services`
--

CREATE TABLE `services` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `description` text DEFAULT NULL,
  `price` decimal(10,2) NOT NULL,
  `duration` int(11) NOT NULL COMMENT 'Duration in minutes',
  `active` tinyint(1) DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `services`
--

INSERT INTO `services` (`id`, `name`, `description`, `price`, `duration`, `active`, `created_at`, `updated_at`) VALUES
(1, 'Basic Wash', 'Exterior wash with hand drying', 19.99, 30, 1, '2025-05-08 15:06:38', '2025-05-08 15:06:38'),
(2, 'Full Interior Clean', 'Vacuum, wipe down all surfaces, window cleaning', 49.99, 60, 1, '2025-05-08 15:06:38', '2025-05-08 15:06:38'),
(3, 'Premium Detail', 'Complete interior and exterior detailing', 149.99, 180, 1, '2025-05-08 15:06:38', '2025-05-08 15:06:38'),
(4, 'Express Wax', 'Quick wax application for shine and protection', 29.99, 45, 1, '2025-05-08 15:06:38', '2025-05-08 15:06:38'),
(5, 'Engine Bay Detail', 'Cleaning and dressing of engine compartment', 89.99, 90, 1, '2025-05-08 15:06:38', '2025-05-08 15:06:38'),
(6, 'Taga Hugas', 'Testing', 1499.99, 15, 1, '2025-05-10 14:57:48', '2025-05-10 14:58:03'),
(7, 'Wipemarks & Watermarks Removal', 'Eliminate stubborn stains and restore crystal-clear surfaces.', 150.00, 20, 1, '2025-05-10 16:20:18', '2025-05-10 16:20:18'),
(8, 'Ceramic Coating', 'Long-lasting protection with a brilliant, hydrophobic finish.', 150.00, 30, 1, '2025-05-10 16:20:33', '2025-05-10 16:20:33'),
(9, 'Exterior Detailing', 'Deep-clean and enhance your vehicle’s outer appearance.', 1500.00, 60, 1, '2025-05-10 16:20:55', '2025-05-10 16:20:55'),
(10, 'Interior Detailing', 'Revitalize your car\'s interior with precision cleaning and conditioning.', 500.00, 45, 1, '2025-05-10 16:21:07', '2025-05-10 16:21:07'),
(11, 'Headlight Restoration', 'Improve visibility and safety by restoring cloudy headlights.', 999.00, 120, 1, '2025-05-10 16:21:21', '2025-05-10 16:21:21'),
(12, 'Back to Zero', 'Full reset detailing to restore your car to showroom condition.', 9999.00, 120, 1, '2025-05-10 16:21:39', '2025-05-10 16:21:39'),
(13, 'Panel Paint', 'Touch-ups or full panel repainting for consistent color and finish.', 12345.00, 20, 1, '2025-05-10 16:21:52', '2025-05-10 16:21:52'),
(14, 'Paint Correction', 'Remove swirl marks, light scratches, and oxidation for a flawless shine.', 1250.00, 45, 1, '2025-05-10 16:22:05', '2025-05-10 16:22:05');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `password` varchar(255) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `role` enum('admin','user') NOT NULL DEFAULT 'user',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `customer_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `password`, `name`, `email`, `role`, `created_at`, `customer_id`) VALUES
(1, 'admin123', 'Admin User', 'admin@admin.com', 'admin', '2025-05-08 15:06:38', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `vehicles`
--

CREATE TABLE `vehicles` (
  `id` int(11) NOT NULL,
  `customer_id` int(11) NOT NULL,
  `make` varchar(50) NOT NULL,
  `model` varchar(50) NOT NULL,
  `year` int(11) DEFAULT NULL,
  `license_plate` varchar(20) DEFAULT NULL,
  `color` varchar(30) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `vehicles`
--

INSERT INTO `vehicles` (`id`, `customer_id`, `make`, `model`, `year`, `license_plate`, `color`, `created_at`, `updated_at`) VALUES
(1, 1, 'Honda', 'Accord', 2018, 'ABC123', 'Black', '2025-05-08 15:06:38', '2025-05-08 15:06:38'),
(2, 1, 'Toyota', 'Camry', 2020, 'XYZ789', 'Silver', '2025-05-08 15:06:38', '2025-05-08 15:06:38'),
(3, 2, 'Ford', 'Mustang', 2019, 'FAST01', 'Red', '2025-05-08 15:06:38', '2025-05-08 15:06:38'),
(4, 3, 'Chevrolet', 'Malibu', 2017, 'BOB555', 'Blue', '2025-05-08 15:06:38', '2025-05-08 15:06:38');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `appointments`
--
ALTER TABLE `appointments`
  ADD PRIMARY KEY (`id`),
  ADD KEY `customer_id` (`customer_id`),
  ADD KEY `vehicle_id` (`vehicle_id`),
  ADD KEY `service_id` (`service_id`);

--
-- Indexes for table `customers`
--
ALTER TABLE `customers`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `services`
--
ALTER TABLE `services`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_customer` (`customer_id`);

--
-- Indexes for table `vehicles`
--
ALTER TABLE `vehicles`
  ADD PRIMARY KEY (`id`),
  ADD KEY `customer_id` (`customer_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `appointments`
--
ALTER TABLE `appointments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `customers`
--
ALTER TABLE `customers`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `services`
--
ALTER TABLE `services`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `vehicles`
--
ALTER TABLE `vehicles`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `appointments`
--
ALTER TABLE `appointments`
  ADD CONSTRAINT `appointments_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `appointments_ibfk_2` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `appointments_ibfk_3` FOREIGN KEY (`service_id`) REFERENCES `services` (`id`);

--
-- Constraints for table `users`
--
ALTER TABLE `users`
  ADD CONSTRAINT `fk_customer` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`);

--
-- Constraints for table `vehicles`
--
ALTER TABLE `vehicles`
  ADD CONSTRAINT `vehicles_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
