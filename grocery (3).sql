-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 17, 2026 at 02:52 PM
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
-- Database: `grocery`
--

-- --------------------------------------------------------

--
-- Table structure for table `employees`
--

CREATE TABLE `employees` (
  `EmpID` int(11) NOT NULL,
  `FirstName` varchar(100) NOT NULL,
  `LastName` varchar(100) NOT NULL,
  `Email` varchar(150) NOT NULL,
  `Gender` varchar(20) DEFAULT NULL,
  `DOB` date DEFAULT NULL,
  `ContactNo` varchar(20) DEFAULT NULL,
  `EmpType` varchar(50) DEFAULT NULL,
  `Education` varchar(100) DEFAULT NULL,
  `Address` varchar(255) DEFAULT NULL,
  `DOJ` date DEFAULT NULL,
  `Salary` decimal(10,2) DEFAULT NULL,
  `Role` varchar(50) NOT NULL,
  `Password` varchar(255) NOT NULL,
  `Archived` tinyint(4) DEFAULT 0,
  `CreatedAt` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `employees`
--

INSERT INTO `employees` (`EmpID`, `FirstName`, `LastName`, `Email`, `Gender`, `DOB`, `ContactNo`, `EmpType`, `Education`, `Address`, `DOJ`, `Salary`, `Role`, `Password`, `Archived`, `CreatedAt`) VALUES
(1, 'Admin', 'User', 'admin@grocery.com', 'Male', '1990-01-15', '09123456789', 'Regular', 'Bachelor', '123 Admin St.', '2026-06-17', 50000.00, 'Admin', 'admin123', 0, '2026-06-17 12:35:12'),
(2, 'John', 'Cashier', 'cashier@grocery.com', 'Male', '1995-05-20', '09123456790', 'Regular', 'Senior High School', '456 Cashier Ave.', '2026-06-17', 15000.00, 'Cashier', 'cashier123', 0, '2026-06-17 12:35:13');

-- --------------------------------------------------------

--
-- Table structure for table `product`
--

CREATE TABLE `product` (
  `PrID` int(11) NOT NULL,
  `PrName` varchar(150) NOT NULL,
  `PrBrand` varchar(100) DEFAULT NULL,
  `Category` varchar(100) DEFAULT NULL,
  `Price` decimal(10,2) NOT NULL,
  `Quantity` int(11) DEFAULT 0,
  `Availability` varchar(50) DEFAULT 'Available',
  `ShelfLife` date DEFAULT NULL,
  `SupplierID` int(11) DEFAULT NULL,
  `IsArchived` tinyint(4) DEFAULT 0,
  `CreatedAt` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `product`
--

INSERT INTO `product` (`PrID`, `PrName`, `PrBrand`, `Category`, `Price`, `Quantity`, `Availability`, `ShelfLife`, `SupplierID`, `IsArchived`, `CreatedAt`) VALUES
(1, 'Jasmine Rice 5kg', 'Gold Premium', 'Rice and Grains', 250.00, 50, 'Available', '2026-12-31', 1, 0, '2026-06-17 12:35:13'),
(2, 'Banana Catsup 320ml', 'Del Monte', 'Condiments and Sauces', 35.00, 100, 'Available', '2026-06-30', 2, 0, '2026-06-17 12:35:13'),
(3, 'Fresh Milk 1L', 'Brand X', 'Dairy Products', 85.00, 30, 'Available', '2025-07-20', 3, 0, '2026-06-17 12:35:13'),
(4, 'Instant Noodles Pack', 'Lucky Me', 'Instant Noodles and Ready Meals', 12.00, 200, 'Available', '2026-12-31', 2, 0, '2026-06-17 12:35:13'),
(5, 'Cooking Oil 1L', 'Paraf', 'Cooking Oil and Spices', 95.00, 45, 'Available', '2027-01-15', 1, 0, '2026-06-17 12:35:13'),
(6, 'Canned Tuna 180g', 'Century', 'Canned and Packaged Goods', 45.00, 80, 'Available', '2026-08-20', 2, 0, '2026-06-17 12:35:13'),
(7, 'Fresh Tomatoes 1kg', 'Local Farm', 'Vegetables', 60.00, 25, 'Available', '2025-07-10', 1, 0, '2026-06-17 12:35:13'),
(8, 'Cheese 200g', 'Dairy Queen', 'Dairy Products', 120.00, 20, 'Available', '2025-12-01', 3, 0, '2026-06-17 12:35:13'),
(9, 'Bread Loaf', 'Golden Bake', 'Bread and Bakery', 50.00, 35, 'Available', '2025-07-15', 3, 0, '2026-06-17 12:35:13'),
(10, 'Soft Drinks 1.5L', 'Soda Brand', 'Beverages', 65.00, 60, 'Available', '2025-12-31', 2, 0, '2026-06-17 12:35:13');

-- --------------------------------------------------------

--
-- Table structure for table `sales`
--

CREATE TABLE `sales` (
  `SaleID` int(11) NOT NULL,
  `BillNo` varchar(50) NOT NULL,
  `SaleDate` date NOT NULL,
  `SaleTime` time DEFAULT NULL,
  `CashierID` int(11) NOT NULL,
  `CustomerName` varchar(150) DEFAULT NULL,
  `CustomerContact` varchar(20) DEFAULT NULL,
  `TotalAmount` decimal(12,2) NOT NULL,
  `PaymentMethod` varchar(50) DEFAULT NULL,
  `CreatedAt` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `salesitems`
--

CREATE TABLE `salesitems` (
  `ItemID` int(11) NOT NULL,
  `SaleID` int(11) NOT NULL,
  `ProductID` int(11) NOT NULL,
  `Quantity` int(11) NOT NULL,
  `UnitPrice` decimal(10,2) NOT NULL,
  `Total` decimal(12,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `supplier`
--

CREATE TABLE `supplier` (
  `SupID` int(11) NOT NULL,
  `InvoiceNo` varchar(100) NOT NULL,
  `Name` varchar(150) NOT NULL,
  `Contact` varchar(20) DEFAULT NULL,
  `Description` text DEFAULT NULL,
  `IsArchived` tinyint(4) DEFAULT 0,
  `CreatedAt` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `supplier`
--

INSERT INTO `supplier` (`SupID`, `InvoiceNo`, `Name`, `Contact`, `Description`, `IsArchived`, `CreatedAt`) VALUES
(1, 'SUP001', 'Fresh Produce Co.', '09123456701', 'Fresh vegetables and fruits supplier', 0, '2026-06-17 12:35:13'),
(2, 'SUP002', 'Global Imports Inc.', '09123456702', 'International food products distributor', 0, '2026-06-17 12:35:13'),
(3, 'SUP003', 'Local Dairy Farm', '09123456703', 'Fresh dairy and milk products', 0, '2026-06-17 12:35:13');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `employees`
--
ALTER TABLE `employees`
  ADD PRIMARY KEY (`EmpID`),
  ADD UNIQUE KEY `Email` (`Email`),
  ADD KEY `idx_emp_email` (`Email`),
  ADD KEY `idx_emp_role` (`Role`);

--
-- Indexes for table `product`
--
ALTER TABLE `product`
  ADD PRIMARY KEY (`PrID`),
  ADD KEY `SupplierID` (`SupplierID`),
  ADD KEY `idx_prod_category` (`Category`),
  ADD KEY `idx_prod_availability` (`Availability`);

--
-- Indexes for table `sales`
--
ALTER TABLE `sales`
  ADD PRIMARY KEY (`SaleID`),
  ADD UNIQUE KEY `BillNo` (`BillNo`),
  ADD KEY `idx_sales_date` (`SaleDate`),
  ADD KEY `idx_sales_cashier` (`CashierID`);

--
-- Indexes for table `salesitems`
--
ALTER TABLE `salesitems`
  ADD PRIMARY KEY (`ItemID`),
  ADD KEY `SaleID` (`SaleID`),
  ADD KEY `ProductID` (`ProductID`);

--
-- Indexes for table `supplier`
--
ALTER TABLE `supplier`
  ADD PRIMARY KEY (`SupID`),
  ADD UNIQUE KEY `InvoiceNo` (`InvoiceNo`),
  ADD KEY `idx_sup_name` (`Name`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `employees`
--
ALTER TABLE `employees`
  MODIFY `EmpID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `product`
--
ALTER TABLE `product`
  MODIFY `PrID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `sales`
--
ALTER TABLE `sales`
  MODIFY `SaleID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `salesitems`
--
ALTER TABLE `salesitems`
  MODIFY `ItemID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `supplier`
--
ALTER TABLE `supplier`
  MODIFY `SupID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `product`
--
ALTER TABLE `product`
  ADD CONSTRAINT `product_ibfk_1` FOREIGN KEY (`SupplierID`) REFERENCES `supplier` (`SupID`);

--
-- Constraints for table `sales`
--
ALTER TABLE `sales`
  ADD CONSTRAINT `sales_ibfk_1` FOREIGN KEY (`CashierID`) REFERENCES `employees` (`EmpID`);

--
-- Constraints for table `salesitems`
--
ALTER TABLE `salesitems`
  ADD CONSTRAINT `salesitems_ibfk_1` FOREIGN KEY (`SaleID`) REFERENCES `sales` (`SaleID`),
  ADD CONSTRAINT `salesitems_ibfk_2` FOREIGN KEY (`ProductID`) REFERENCES `product` (`PrID`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
