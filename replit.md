# dabba - Logistics Platform

## Overview

dabba is a web-based logistics platform that connects senders with transporters for shipping services. Built with Flask and SQLAlchemy, it provides a marketplace-style interface where senders can post shipment requests and transporters can browse and book available shipments. The platform includes features for tracking, payments, reviews, and real-time updates.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database ORM**: SQLAlchemy with declarative base models
- **Authentication**: Flask-Login for session management
- **Forms**: WTForms with Flask-WTF for form handling and validation
- **Database**: SQLite (default) with environment-based configuration for production databases

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default)
- **CSS Framework**: Bootstrap 5.3.0 for responsive design
- **Icons**: Font Awesome 6.4.0 for iconography
- **JavaScript**: Vanilla JavaScript with Bootstrap components
- **Design Philosophy**: Minimal, Apple/Airbnb-inspired aesthetic

### Authentication & Authorization
- **User Management**: Flask-Login with password hashing via Werkzeug
- **User Types**: Enum-based role system (Sender/Transporter)
- **Session Management**: Server-side sessions with configurable secret keys

## Key Components

### Database Models
- **User**: Stores user accounts with role-based access (sender/transporter)
- **Shipment**: Core entity representing shipping requests with status tracking
- **TrackingUpdate**: GPS coordinates and status updates for shipments
- **Payment**: Payment transaction records
- **Review**: Rating and feedback system between users

### Core Features
1. **User Registration & Authentication**: Unified accounts with OAuth social login (Google, Apple, Facebook)
2. **Shipment Management**: Create, browse, and book shipment requests
3. **Real-time GPS Tracking**: Complete GPS tracking system with live position updates, reverse geocoding, speed/accuracy monitoring, and background tracking
4. **Payment Processing**: Mock payment system with transaction management
5. **Review System**: Star-based rating system with comments and reviews display
6. **Messaging System**: WhatsApp-style chat interface for shipment communication
7. **Mobile Navigation**: Bottom navigation bar with 5 sections for mobile-first experience
8. **Profile Management**: Modern dark theme profile with statistics and connected accounts

### Form Validation
- **Login/Registration**: Email validation, password strength requirements
- **Shipment Creation**: Location validation, weight limits, date validation
- **Payment Processing**: Card validation, expiry date checking
- **Review System**: Rating constraints, comment length validation

## Data Flow

### Shipment Lifecycle
1. **Creation**: Sender posts shipment with pickup/delivery details
2. **Discovery**: Transporters browse available shipments
3. **Booking**: Transporter submits booking request with proposed price
4. **Payment**: Sender processes payment for accepted booking
5. **Tracking**: Real-time GPS updates during transport
6. **Completion**: Delivery confirmation and review exchange

### User Interactions
- **Senders**: Post shipments → Review proposals → Make payments → Track progress → Leave reviews
- **Transporters**: Browse shipments → Submit proposals → Provide tracking → Receive payments → Leave reviews

## External Dependencies

### Frontend Libraries
- **Bootstrap 5.3.0**: UI framework for responsive design
- **Font Awesome 6.4.0**: Icon library for visual elements
- **Custom CSS**: Apple/Airbnb-inspired minimal design system

### Backend Dependencies
- **Flask**: Core web framework
- **Flask-SQLAlchemy**: Database ORM integration
- **Flask-Login**: User session management
- **Flask-WTF**: Form handling and CSRF protection
- **WTForms**: Form validation and rendering
- **Werkzeug**: Password hashing and security utilities
- **Authlib**: OAuth integration for social authentication
- **Requests**: HTTP client for API calls

### Utility Functions
- **Mock Services**: GPS coordinate generation, distance calculation, transaction ID generation
- **Formatting**: Currency display, status color coding, user type display

## Deployment Strategy

### Environment Configuration
- **Database**: Environment-variable based database URL configuration
- **Security**: Configurable session secrets via environment variables
- **Development**: SQLite for local development
- **Production**: PostgreSQL-ready configuration

### WSGI Configuration
- **ProxyFix**: Configured for deployment behind reverse proxies
- **Debug Mode**: Environment-based debug configuration
- **Host Binding**: Configured for containerized deployment (0.0.0.0:5000)

### Static Assets
- **CSS/JS**: Served via Flask's static file handling
- **CDN Integration**: Bootstrap and Font Awesome served via CDN
- **Custom Assets**: Local CSS and JavaScript for platform-specific functionality

## Changelog
- July 03, 2025. Initial setup with ShipConnect branding
- July 03, 2025. Renamed application to "dabba" per user request
- July 09, 2025. Updated color scheme to pastel green-blue theme
- July 09, 2025. Complete Italian translation of all interface elements
- July 09, 2025. Integrated custom dabba logo throughout the application
- July 09, 2025. Added dark theme with same verde acqua and blue color palette
- July 09, 2025. Implemented real GPS integration with live tracking using Geolocation API
- July 09, 2025. Implemented flexible user model: single account can both send and transport packages
- July 11, 2025. Added comprehensive messaging system with WhatsApp-style interface
- July 11, 2025. Implemented mobile bottom navigation bar with 5 sections (Home, Cerca, Pubblica, Messaggi, Profilo)
- July 11, 2025. Created modern profile page with dark theme, ratings, and reviews system
- July 11, 2025. Integrated OAuth social authentication for Google, Apple, and Facebook
- July 13, 2025. Fixed login 500 error by removing user_type database constraint
- July 13, 2025. Implemented complete real GPS tracking system with live position updates, reverse geocoding, and background tracking
- July 13, 2025. Replaced direct booking system with request/acceptance workflow for better control and communication
- July 13, 2025. Fixed messaging system - "Contact" buttons now properly open chat interface with correct user IDs
- July 13, 2025. Added ShipmentRequest model with proposed pricing, messaging, and status management
- July 13, 2025. Created comprehensive request management interface for senders to accept/reject transport requests
- July 14, 2025. Integrated Replit Auth replacing custom login system for seamless authentication
- July 14, 2025. Updated User model to use String IDs compatible with Replit's authentication system
- July 14, 2025. Created landing page for logged-out users with Replit login integration
- July 14, 2025. Added OAuth model for session storage and updated all foreign key relationships
- July 14, 2025. Added request recap/summary screen for shipment requests with price comparison and detailed overview
- July 14, 2025. Reverted to traditional email/password authentication system per user request
- July 14, 2025. Created modern login and registration templates with responsive design and password visibility toggle
- July 15, 2025. Updated logo with new light theme version provided by user
- July 15, 2025. Removed dark theme functionality and converted app to light theme only

## User Preferences

Preferred communication style: Simple, everyday language.
App name: dabba (updated from ShipConnect)
Language: Italian interface
Design: Pastel green-blue color scheme (verde acqua e blu)
User model: Flexible - single account can both send and transport packages