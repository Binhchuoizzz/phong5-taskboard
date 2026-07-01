import sys
from django.contrib.auth import get_user_model
from django.db import transaction
from plane.license.models import Instance, InstanceAdmin
from plane.db.models import Workspace, WorkspaceMember, Project, ProjectMember, ProjectIdentifier, State, Label

User = get_user_model()

try:
    with transaction.atomic():
        # 1. Create or get Admin user
        admin_email = "admin@sentinel.local"
        admin_user = User.objects.filter(email=admin_email).first()
        if not admin_user:
            admin_user = User.objects.create_user(
                email=admin_email,
                password="Sentinel@123",
                username="admin",
                first_name="Admin",
                last_name="System",
                is_superuser=True,
                is_staff=True,
                is_email_verified=True
            )
            print(f"Created admin user: {admin_email}")
        else:
            admin_user.set_password("Sentinel@123")
            admin_user.is_superuser = True
            admin_user.is_staff = True
            admin_user.is_email_verified = True
            admin_user.first_name = "Admin"
            admin_user.last_name = "System"
            admin_user.save()
            print(f"Updated admin user: {admin_email}")

        # 2. Promote to InstanceAdmin and complete setup status
        instance = Instance.objects.last()
        if instance:
            _, created = InstanceAdmin.objects.get_or_create(
                user=admin_user,
                instance=instance,
                role=20 # Admin
            )
            if created:
                print("Promoted admin user to Instance Admin role.")
            instance.is_setup_done = True
            instance.is_signup_screen_visited = True
            instance.save()
            print("Set instance setup flags (is_setup_done, is_signup_screen_visited) to True.")
        else:
            print("Warning: No Instance object found in database!")

        # 3. Create Workspace
        workspace_slug = "sentinel"
        workspace = Workspace.objects.filter(slug=workspace_slug).first()
        if not workspace:
            workspace = Workspace.objects.create(
                name="Sentinel-Workspace",
                slug=workspace_slug,
                owner=admin_user,
                organization_size="5000"
            )
            print(f"Created workspace: {workspace.name} (slug: {workspace_slug})")
        else:
            print(f"Workspace {workspace_slug} already exists.")

        # 4. Add admin to WorkspaceMember
        member, created = WorkspaceMember.objects.get_or_create(
            workspace=workspace,
            member=admin_user,
            defaults={"role": 20} # Admin
        )
        if created:
            print("Added admin user as Admin member of the workspace.")
        else:
            member.role = 20
            member.save()

        # 5. Define projects to create
        projects_data = [
            ("PRJ1-Core", "PRJ1", "Core Platform — Architecture, API foundations & system coordination"),
            ("PRJ2-Security", "PRJ2", "Security Compliance — GRC, policy, risk assessment"),
            ("PRJ3-DevOps", "PRJ3", "Infrastructure & DevOps — CI/CD, deployment, network management"),
            ("PRJ4-QA", "PRJ4", "Quality Assurance — Pentest, red team, vulnerability assessment"),
            ("PRJ5-Integrations", "PRJ5", "System Integrations — Webhooks, API connectors, tech deployment"),
            ("PRJ6-Analytics", "PRJ6", "Threat Analytics — Incident response, monitoring, SIEM"),
            ("PRJ7-AI", "PRJ7", "AI Engine — ML models, AI security research & automation"),
        ]

        for name, identifier, desc in projects_data:
            project = Project.objects.filter(workspace=workspace, name=name).first()
            if not project:
                project = Project.objects.create(
                    workspace=workspace,
                    name=name,
                    identifier=identifier,
                    description=desc,
                    project_lead=admin_user,
                    network=0 # Secret/Private
                )
                # Create ProjectIdentifier
                ProjectIdentifier.objects.get_or_create(
                    workspace=workspace,
                    project=project,
                    name=identifier
                )
                # Add Admin to ProjectMember
                ProjectMember.objects.get_or_create(
                    project=project,
                    member=admin_user,
                    defaults={"role": 20}
                )
                print(f"Created Project: {name} (Identifier: {identifier})")
            else:
                print(f"Project {name} already exists.")

            # 6. Define custom workflow states for specific projects
            if identifier == "PRJ6": # Threat Analytics (Incident Response)
                states = [
                    ("Detected", "#EF4444", "backlog", True),
                    ("Triaging", "#F59E0B", "unstarted", False),
                    ("Investigating", "#3B82F6", "started", False),
                    ("Containment", "#10B981", "started", False),
                    ("Eradication", "#8B5CF6", "started", False),
                    ("Recovery", "#EC4899", "started", False),
                    ("Post-Mortem", "#6B7280", "started", False),
                    ("Closed", "#10B981", "completed", False),
                ]
            elif identifier == "PRJ4": # Quality Assurance (Pentesting)
                states = [
                    ("Scoping", "#6B7280", "backlog", True),
                    ("Reconnaissance", "#3B82F6", "unstarted", False),
                    ("Exploitation", "#EF4444", "started", False),
                    ("Reporting", "#F59E0B", "started", False),
                    ("Remediation Verify", "#8B5CF6", "started", False),
                    ("Closed", "#10B981", "completed", False),
                ]
            else: # General projects
                states = [
                    ("Backlog", "#60646C", "backlog", True),
                    ("Todo", "#60646C", "unstarted", False),
                    ("In Progress", "#F59E0B", "started", False),
                    ("In Review", "#8B5CF6", "started", False),
                    ("Testing", "#3B82F6", "started", False),
                    ("Done", "#46A758", "completed", False),
                    ("Cancelled", "#9AA4BC", "cancelled", False),
                ]

            # Clear existing states for this project to make sure the workflows match exactly
            State.all_state_objects.filter(project=project).delete()

            seq = 10000
            for state_name, color, group, is_default in states:
                state = State.all_state_objects.create(
                    project=project,
                    workspace=workspace,
                    name=state_name,
                    color=color,
                    group=group,
                    default=is_default,
                    sequence=seq
                )
                if is_default:
                    project.default_state = state
                    project.save()
                seq += 10000

        # 7. Create Workspace Labels
        labels_data = [
            # Priority
            ("P0-Critical", "#EF4444", "Priority: Critical Severity"),
            ("P1-High", "#F97316", "Priority: High Severity"),
            ("P2-Medium", "#EAB308", "Priority: Medium Severity"),
            ("P3-Low", "#22C55E", "Priority: Low Severity"),
            # Type
            ("Bug", "#EF4444", "Software defects or system issues"),
            ("Feature", "#3B82F6", "New requests or enhancements"),
            ("Incident", "#F43F5E", "Security incidents"),
            ("Audit", "#8B5CF6", "System audits"),
            ("Compliance", "#EC4899", "Policy & Compliance"),
            ("Research", "#10B981", "R&D activities"),
            ("Deployment", "#06B6D4", "Production deployment tasks"),
            ("Task", "#6B7280", "General tasks"),
            # Security
            ("Confidential", "#EF4444", "Highly confidential information"),
            ("Internal", "#F97316", "Internal use only"),
            ("Public", "#22C55E", "Public information"),
        ]

        for label_name, color, desc in labels_data:
            label = Label.objects.filter(workspace=workspace, project=None, name=label_name).first()
            if not label:
                Label.objects.create(
                    workspace=workspace,
                    project=None,
                    name=label_name,
                    color=color,
                    description=desc
                )
                print(f"Created Workspace Label: {label_name}")
            else:
                label.color = color
                label.description = desc
                label.save()

        # 8. Disable public registration (Phase 4.10)
        from plane.license.models import InstanceConfiguration
        config, created = InstanceConfiguration.objects.get_or_create(key="ENABLE_SIGNUP")
        config.value = "0"
        config.save()
        print("Disabled public registration (signup). Only invited users can register.")

        # 9. Create Mock Users for RBAC testing
        mock_users = [
            ("member1@sentinel.local", "member1", "Analytics", "Member 1", 15, "PRJ6-Analytics"),
            ("guest1@sentinel.local", "guest1", "Core", "Guest 1", 5, "PRJ1-Core")
        ]

        for email, username, first_name, last_name, role_val, project_name in mock_users:
            user = User.objects.filter(email=email).first()
            if not user:
                user = User.objects.create_user(
                    email=email,
                    password="Sentinel@123",
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    is_email_verified=True
                )
                print(f"Created mock user: {email}")
            else:
                user.set_password("Sentinel@123")
                user.first_name = first_name
                user.last_name = last_name
                user.save()

            # Add to workspace
            w_member, w_created = WorkspaceMember.objects.get_or_create(
                workspace=workspace,
                member=user,
                defaults={"role": role_val}
            )
            if not w_created:
                w_member.role = role_val
                w_member.save()

            # Add to project
            proj = Project.objects.filter(workspace=workspace, name=project_name).first()
            if proj:
                p_member, p_created = ProjectMember.objects.get_or_create(
                    project=proj,
                    member=user,
                    defaults={"role": role_val}
                )
                if not p_created:
                    p_member.role = role_val
                    p_member.save()
                print(f"Assigned user {email} to project {project_name} as role {role_val}.")

        print("Successfully initialized all workspace projects, states, labels, and RBAC mock members!")

except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
