import json
from django.test import TestCase
from django.core.urlresolvers import reverse
from django_fixmystreet.fixmystreet.models import OrganisationEntity, UserOrganisationMembership, FMSUser


class GroupsTest(TestCase):

    fixtures = ["bootstrap","list_items"]

    def setUp(self):
        self.manager = FMSUser(
            telephone="0123456789",
            last_used_language="fr",
            password='test',
            first_name="manager",
            last_name="manager",
            email="manager@a.com",
            manager=True
        )
        self.manager.set_password('test')
        self.manager.organisation = OrganisationEntity.objects.get(pk=14)
        self.manager.save()

        self.leader = FMSUser(
            telephone="0123456789",
            last_used_language="fr",
            password='test',
            first_name="leader",
            last_name="leader",
            email="leader@a.com",
            manager=True,
            leader = True
        )
        self.leader.set_password('test')
        self.leader.organisation = OrganisationEntity.objects.get(pk=14)
        self.leader.save()

        self.group1 = OrganisationEntity(
            name_fr="groupe1",
            name_nl="groep1",
            phone="00000000",
            email="group@test.be",
            type='D',
            dependency=OrganisationEntity.objects.get(pk=14)
        )
        self.group1.save();

        self.group2 = OrganisationEntity(
            name_fr="groupe2",
            name_nl="groep2",
            phone="00000000",
            email="group2@test.be",
            type='D',
            dependency=OrganisationEntity.objects.get(pk=11)
        )
        self.group2.save();

        self.creategroup_post = {
            'name_fr':'groupe3',
            'name_nl':'groep3',
            'phone':'0000000000',
            'email':'group3@test.com',
            'type':'D'
        }

        self.creategroup_post2 = {
            'name_fr':'groupe4',
            'name_nl':'groep4',
            'phone':'0000000000',
            'email':'group4@test.com',
            'type':'S'
        }

        self.editgroup_post = {
            'name_fr':'groupe1nouveau',
            'name_nl':'groep1nieuw',
            'phone':'111111',
            'email':'group1new@test.com',
            'type':'D'
        }
        self.editgroup_post2 = {
            'name_fr':'groupe2nouveau',
            'name_nl':'groep2nieuw',
            'phone':'2222222',
            'email':'group2new@test.com',
            'type':'S'
        }

    def testListGroups(self):
        self.client.login(username='manager@a.com', password='test')
        response = self.client.post(reverse('list_groups'), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTrue('groups' in response.context)
        self.assertTrue('can_create' in response.context)
        can_create = response.context['can_create']
        #This user should not be able to create
        groups = response.context['groups']
        self.assertFalse(can_create)
        #now check that all groups are groups of organisation should only be group1 as the other is assigned to other entity

        #check to see only your groups is back enabled
        self.assertEquals(groups.count(), 1)
        self.assertEquals(self.group1, groups[0])
        #now do same test with leader user the result should be the same only can_create has to be true
        self.client.logout()
        self.client.login(username='leader@a.com', password='test')
        response = self.client.post(reverse('list_groups'), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTrue('groups' in response.context)
        self.assertTrue('can_create' in response.context)
        can_create = response.context['can_create']
        #This user should not be able to create
        groups = response.context['groups']
        self.assertTrue(can_create)
        #now check that all groups are groups of organisation should only be group1 as the other is assigned to other entity
        #test if the security to show only groups of your organisation is enabled
        self.assertEquals(groups.count(), 1)
        self.assertEquals(self.group1, groups[0])

    def testCreateGroups(self):
        self.client.login(username='leader@a.com', password='test')
        response = self.client.post(reverse('create_group'), self.creategroup_post)
        self.assertEquals(response.status_code, 302)
        response = self.client.post(reverse('list_groups'), follow=True)

        #now check if we have 2 groups and that the 2nd is group3
        self.assertEquals(response.status_code, 200)
        self.assertTrue('groups' in response.context)
        self.assertTrue('can_create' in response.context)
        groups = response.context['groups']
        can_create = response.context['can_create']
        self.assertTrue(can_create)

        #check to see only your organisation's groups is enabled again also update the number of the element we get from the array
        self.assertEquals(groups.count(), 2)

        if groups[0].name_fr == 'groupe3':
            group = groups[0]
        else:
            group = groups[1]

        self.assertEquals(group.name_fr, 'groupe3')
        self.assertEquals(group.name_nl, 'groep3')
        self.assertEquals(group.phone, '0000000000')
        self.assertEquals(group.email, 'group3@test.com')
        self.assertEquals(group.type, 'D')
        self.assertEquals(group.dependency, self.leader.organisation)

        #now test create with user who is not leader
        self.client.logout()
        self.client.login(username='manager@a.com', password='test')
        response = self.client.post(reverse('create_group'), self.creategroup_post2)
        self.assertEquals(response.status_code, 200)
        response = self.client.post(reverse('list_groups'), follow=True)

        #now check if we have 2 groups and that the 2nd is group3
        self.assertEquals(response.status_code, 200)
        self.assertTrue('groups' in response.context)
        self.assertTrue('can_create' in response.context)
        can_create = response.context['can_create']
        self.assertFalse(can_create)
        groups = response.context['groups']

        self.assertEquals(groups.count(), 2)

    def testEditGroups(self):
        self.client.login(username='leader@a.com', password='test')
        response = self.client.post(reverse('edit_group', args=[self.group1.id]), self.editgroup_post)
        self.assertEquals(response.status_code, 302)
        response = self.client.post(reverse('list_groups'), follow=True)

        #now check if we have 2 groups and that the 2nd is group3
        self.assertEquals(response.status_code, 200)
        self.assertTrue('groups' in response.context)
        self.assertTrue('can_create' in response.context)
        groups = response.context['groups']
        can_create = response.context['can_create']
        self.assertTrue(can_create)
        self.assertEquals(groups.count(), 1)
        self.assertEquals(groups[0].name_fr, 'groupe1nouveau')
        self.assertEquals(groups[0].name_nl, 'groep1nieuw')
        self.assertEquals(groups[0].phone, '111111')
        self.assertEquals(groups[0].email, 'group1new@test.com')
        self.assertEquals(groups[0].type, 'D')
        self.assertEquals(groups[0].dependency, self.leader.organisation)

        #now do the test with a non leader
        self.client.logout()
        self.client.login(username='manager@a.com', password='test')
        response = self.client.post(reverse('edit_group', args=[self.group1.id]), self.editgroup_post2)
        self.assertEquals(response.status_code, 200)
        response = self.client.post(reverse('list_groups'), follow=True)

        #now check if we have 1 group that depends of my organisation
        self.assertEquals(response.status_code, 200)
        self.assertTrue('groups' in response.context)
        self.assertTrue('can_create' in response.context)
        groups = response.context['groups']
        can_create = response.context['can_create']
        self.assertFalse(can_create)
        self.assertEquals(groups.count(), 1)

        #should still be the same as this user does not have the rights to update groups
        self.assertEquals(groups[0].name_fr, 'groupe1nouveau')
        self.assertEquals(groups[0].name_nl, 'groep1nieuw')
        self.assertEquals(groups[0].phone, '111111')
        self.assertEquals(groups[0].email, 'group1new@test.com')
        self.assertEquals(groups[0].type, 'D')
        self.assertEquals(groups[0].dependency, self.leader.organisation)

    def testDeleteGroups(self):
        #first try to delete with user who has no permissions
        self.client.login(username='manager@a.com', password='test')
        response = self.client.get(reverse('delete_group', args=[self.group1.id]), follow=True)
        self.assertEquals(response.status_code, 200)
        response = self.client.post(reverse('list_groups'), follow=True)

        #now check if we have 1 group that depends of my organisation
        self.assertEquals(response.status_code, 200)
        self.assertTrue('groups' in response.context)
        self.assertTrue('can_create' in response.context)
        groups = response.context['groups']
        can_create = response.context['can_create']
        self.assertFalse(can_create)
        self.assertEquals(groups.count(), 1)
        self.assertIn(self.group1, groups)

        self.client.logout()

        #now try to delete with user who can
        self.client.login(username='leader@a.com', password='test')
        response = self.client.get(reverse('delete_group', args=[self.group1.id]), follow=True)
        self.assertEquals(response.status_code, 200)
        response = self.client.post(reverse('list_groups'), follow=True)

        #now check if we have 2 groups and that the 2nd is group3
        self.assertEquals(response.status_code, 200)
        self.assertTrue('groups' in response.context)
        self.assertTrue('can_create' in response.context)
        groups = response.context['groups']
        can_create = response.context['can_create']
        self.assertTrue(can_create)
        self.assertEquals(groups.count(), 0)
        self.assertNotIn(self.group1, groups)

    def testAssignMemberToGroup(self):
        #first try to add with user who has not enough rights
        self.client.login(username='manager@a.com', password='test')
        response = self.client.get(reverse('add_membership', args=[self.group1.id, self.manager.id]), follow=True)
        self.assertEquals(response.status_code, 200)
        returnobject = json.loads(str(response.content))
        self.assertTrue('status' in returnobject)
        self.assertFalse('membership_id' in returnobject)
        status = returnobject['status']
        self.assertEquals('Permission Denied', status)

        self.client.logout()
        self.client.login(username='leader@a.com', password='test')
        response = self.client.get(reverse('add_membership', args=[self.group1.id, self.manager.id]), follow=True)
        self.assertEquals(response.status_code, 200)
        returnobject = json.loads(str(response.content))
        self.assertTrue('status' in returnobject)
        self.assertTrue('membership_id' in returnobject)
        status = returnobject['status']
        membership_id = returnobject['membership_id']
        self.assertEquals('OK', status)
        organisationMemberShip = UserOrganisationMembership.objects.get(id=membership_id)
        self.assertEquals(self.manager, organisationMemberShip.user)
        self.assertEquals(self.group1, organisationMemberShip.organisation)

    def testRemoveMemberFromGroup(self):
        #first assign a member to a group
        self.client.login(username='leader@a.com', password='test')
        response = self.client.get(reverse('add_membership', args=[self.group1.id, self.manager.id]), follow=True)
        self.assertEquals(response.status_code, 200)
        returnobject = json.loads(str(response.content))
        self.assertTrue('status' in returnobject)
        self.assertTrue('membership_id' in returnobject)
        status = returnobject['status']
        membership1_id = returnobject['membership_id']
        self.assertEquals('OK', status)

        response = self.client.get(reverse('add_membership', args=[self.group1.id, self.leader.id]), follow=True)
        self.assertEquals(response.status_code, 200)
        returnobject = json.loads(str(response.content))
        self.assertTrue('status' in returnobject)
        self.assertTrue('membership_id' in returnobject)
        membership2_id = returnobject['membership_id']

        self.assertTrue(UserOrganisationMembership.objects.get(id=membership1_id).contact_user)
        self.assertFalse(UserOrganisationMembership.objects.get(id=membership2_id).contact_user)

        #try with user who has no rights to remove it
        self.client.logout()
        self.client.login(username='manager@a.com', password='test')

        response = self.client.get(reverse('remove_membership', args=[membership1_id]), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertIn('Permission Denied', response.content)

        #now try with user who has rights to remove
        self.client.logout()
        self.client.login(username='leader@a.com', password='test')

        response = self.client.get(reverse('remove_membership', args=[membership1_id]), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertNotIn('OK', response.content)  # can not remove contact membership

        response = self.client.get(reverse('remove_membership', args=[membership2_id]), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertIn('OK', response.content)

        self.assertTrue(UserOrganisationMembership.objects.filter(id=membership1_id).exists())
        self.assertFalse(UserOrganisationMembership.objects.filter(id=membership2_id).exists())



