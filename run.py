import os
from app import create_app, db
from app.models import User, Resume, Platform, JobSearchConfig, Application, Subscription, Payment

# Create Flask app
app = create_app()


@app.shell_context_processor
def make_shell_context():
    """Make database models available in Flask shell"""
    return {
        'db': db,
        'User': User,
        'Resume': Resume,
        'Platform': Platform,
        'JobSearchConfig': JobSearchConfig,
        'Application': Application,
        'Subscription': Subscription,
        'Payment': Payment
    }


@app.cli.command()
def seed_platforms():
    """Seed the platforms table with initial data"""
    platforms_data = [
        {'name': 'LinkedIn', 'slug': 'linkedin', 'is_popular': True},
        {'name': 'Indeed', 'slug': 'indeed', 'is_popular': True},
        {'name': 'Glassdoor', 'slug': 'glassdoor', 'is_popular': True},
        {'name': 'Monster', 'slug': 'monster', 'is_popular': False},
        {'name': 'Naukri Gulf', 'slug': 'naukri-gulf', 'is_popular': False},
        {'name': 'Jobble', 'slug': 'jobble', 'is_popular': False},
        {'name': 'Dice', 'slug': 'dice', 'is_popular': False},
        {'name': 'CareerBuilder', 'slug': 'careerbuilder', 'is_popular': False},
        {'name': 'AngelList', 'slug': 'angellist', 'is_popular': False},
        {'name': 'SimplyHired', 'slug': 'simplyhired', 'is_popular': False},
        {'name': 'Remote.co', 'slug': 'remote-co', 'is_popular': False},
        {'name': 'We Work Remotely', 'slug': 'we-work-remotely', 'is_popular': False},
        {'name': 'Stack Overflow Jobs', 'slug': 'stack-overflow-jobs', 'is_popular': False},
        {'name': 'GitHub Jobs', 'slug': 'github-jobs', 'is_popular': False},
        {'name': 'ZipRecruiter', 'slug': 'ziprecruiter', 'is_popular': False},
        {'name': 'FlexJobs', 'slug': 'flexjobs', 'is_popular': False},
    ]

    for platform_data in platforms_data:
        # Check if platform already exists
        existing = Platform.query.filter_by(slug=platform_data['slug']).first()
        if not existing:
            platform = Platform(**platform_data)
            db.session.add(platform)
            print(f"Added platform: {platform_data['name']}")
        else:
            print(f"Platform already exists: {platform_data['name']}")

    db.session.commit()
    print(f"\n✓ Successfully seeded {len(platforms_data)} platforms!")


@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    print("✓ Database initialized!")


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
