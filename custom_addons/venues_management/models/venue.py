from odoo import models, fields


class CommonVenue(models.Model):
    _name = 'artist.venue'
    _description = 'Shared Venues and Event Spaces'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char('Venue Name', required=True, tracking=True)
    venue_type = fields.Selection([
        ('theater', 'Theater'),
        ('gallery', 'Art Gallery'),
        ('concert_hall', 'Concert Hall'),
        ('studio', 'Studio'),
        ('community_center', 'Community Center'),
        ('outdoor_space', 'Outdoor Space'),
        ('museum', 'Museum'),
        ('cultural_center', 'Cultural Center'),
        ('stadium', 'Stadium'),
        ('sports_ground', 'Sports Ground'),
        ('sports_hall', 'Sports Hall'),
        ('school', 'School'),
        ('other', 'Other')
    ], string='Venue Type', required=True, tracking=True)

    address = fields.Text('Address')
    district = fields.Char('District')
    province = fields.Char('Province')
    capacity = fields.Integer('Capacity')

    manager_name = fields.Char('Manager Name')
    manager_phone = fields.Char('Manager Phone')
    manager_email = fields.Char('Manager Email')

    facilities = fields.Text('Available Facilities')
    equipment = fields.Text('Available Equipment')
    accessibility = fields.Boolean('Wheelchair Accessible')
    parking_available = fields.Boolean('Parking Available')

    booking_required = fields.Boolean('Booking Required', default=True)
    booking_contact = fields.Char('Booking Contact')
    rental_rate = fields.Float('Rental Rate per Hour')

    active = fields.Boolean('Active', default=True, tracking=True)
