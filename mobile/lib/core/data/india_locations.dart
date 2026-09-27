class StateUT {
  final String name;
  final String type; // 'State' or 'UT'
  final List<String> districts;

  const StateUT({
    required this.name,
    required this.type,
    required this.districts,
  });
}

class IndiaLocations {
  IndiaLocations._();

  static const List<StateUT> all = [
    // --- 28 STATES ---
    StateUT(
      name: 'Andhra Pradesh',
      type: 'State',
      districts: [
        'Alluri Sitharama Raju', 'Anakapalli', 'Ananthapuramu', 'Annamayya', 'Bapatla',
        'Chittoor', 'Dr. B.R. Ambedkar Konaseema', 'East Godavari', 'Eluru', 'Guntur',
        'Kakinada', 'Krishna', 'Kurnool', 'Nandyal', 'NTR', 'Palnadu', 'Parvathipuram Manyam',
        'Prakasam', 'Sri Potti Sriramulu Nellore', 'Sri Sathya Sai', 'Srikakulam', 'Tirupati',
        'Visakhapatnam', 'Vizianagaram', 'West Godavari', 'YSR Kadapa',
      ],
    ),
    StateUT(
      name: 'Arunachal Pradesh',
      type: 'State',
      districts: [
        'Anjaw', 'Changlang', 'Dibang Valley', 'East Kameng', 'East Siang', 'Itanagar Capital Complex',
        'Kamle', 'Kra Daadi', 'Kurung Kumey', 'Lepa Rada', 'Lohit', 'Longding', 'Lower Dibang Valley',
        'Lower Siang', 'Lower Subansiri', 'Namsai', 'Pakke Kessang', 'Papum Pare', 'Shi Yomi',
        'Siang', 'Tawang', 'Tirap', 'Upper Siang', 'Upper Subansiri', 'West Kameng', 'West Siang',
      ],
    ),
    StateUT(
      name: 'Assam',
      type: 'State',
      districts: [
        'Bajali', 'Baksa', 'Barpeta', 'Biswanath', 'Bongaigaon', 'Cachar', 'Charaideo', 'Chirang',
        'Darrang', 'Dhemaji', 'Dhubri', 'Dibrugarh', 'Dima Hasao', 'Goalpara', 'Golaghat', 'Hailakandi',
        'Hojai', 'Jorhat', 'Kamrup', 'Kamrup Metropolitan', 'Karbi Anglong', 'Karimganj', 'Kokrajhar',
        'Lakhimpur', 'Majuli', 'Morigaon', 'Nagaon', 'Nalbari', 'Sivasagar', 'Sonitpur',
        'South Salmara-Mankachar', 'Tamulpur', 'Tinsukia', 'Udalguri', 'West Karbi Anglong',
      ],
    ),
    StateUT(
      name: 'Bihar',
      type: 'State',
      districts: [
        'Araria', 'Arwal', 'Aurangabad', 'Banka', 'Begusarai', 'Bhagalpur', 'Bhojpur', 'Buxar',
        'Darbhanga', 'East Champaran', 'Gaya', 'Gopalganj', 'Jamui', 'Jehanabad', 'Kaimur',
        'Katihar', 'Khagaria', 'Kishanganj', 'Lakhisarai', 'Madhepura', 'Madhubani', 'Munger',
        'Muzaffarpur', 'Nalanda', 'Nawada', 'Patna', 'Purnia', 'Rohtas', 'Saharsa', 'Samastipur',
        'Saran', 'Sheikhpura', 'Sheohar', 'Sitamarhi', 'Siwan', 'Supaul', 'Vaishali', 'West Champaran',
      ],
    ),
    StateUT(
      name: 'Chhattisgarh',
      type: 'State',
      districts: [
        'Balod', 'Baloda Bazar-Bhatapara', 'Balrampur-Ramanujganj', 'Bastar', 'Bemetara', 'Bijapur',
        'Bilaspur', 'Dantewada', 'Dhamtari', 'Durg', 'Gariaband', 'Gaurela-Pendra-Marwahi', 'Janjgir-Champa',
        'Jashpur', 'Kabirdham', 'Kanker', 'Khairagarh-Chhuikhadan-Gandai', 'Kondagaon', 'Korba', 'Korea',
        'Mahasamund', 'Manendragarh-Chirmiri-Bharatpur', 'Mohla-Manpur-Ambagarh Chowki', 'Mungeli',
        'Narayanpur', 'Raigarh', 'Raipur', 'Rajnandgaon', 'Sakti', 'Sarangarh-Bilaigarh', 'Sukma',
        'Surajpur', 'Surguja',
      ],
    ),
    StateUT(
      name: 'Goa',
      type: 'State',
      districts: ['North Goa', 'South Goa'],
    ),
    StateUT(
      name: 'Gujarat',
      type: 'State',
      districts: [
        'Ahmedabad', 'Amreli', 'Anand', 'Aravalli', 'Banaskantha', 'Bharuch', 'Bhavnagar', 'Botad',
        'Chhota Udaipur', 'Dahod', 'Dang', 'Devbhumi Dwarka', 'Gandhinagar', 'Gir Somnath', 'Jamnagar',
        'Junagadh', 'Kheda', 'Kutch', 'Mahisagar', 'Mehsana', 'Morbi', 'Narmada', 'Navsari', 'Panchmahal',
        'Patan', 'Porbandar', 'Rajkot', 'Sabarkantha', 'Surat', 'Surendranagar', 'Tapi', 'Vadodara', 'Valsad',
      ],
    ),
    StateUT(
      name: 'Haryana',
      type: 'State',
      districts: [
        'Ambala', 'Bhiwani', 'Charkhi Dadri', 'Faridabad', 'Fatehabad', 'Gurugram', 'Hisar', 'Jhajjar',
        'Jind', 'Kaithal', 'Karnal', 'Kurukshetra', 'Mahendragarh', 'Nuh', 'Palwal', 'Panchkula',
        'Panipat', 'Rewari', 'Rohtak', 'Sirsa', 'Sonipat', 'Yamunanagar',
      ],
    ),
    StateUT(
      name: 'Himachal Pradesh',
      type: 'State',
      districts: [
        'Bilaspur', 'Chamba', 'Hamirpur', 'Kangra', 'Kinnaur', 'Kullu', 'Lahaul and Spiti', 'Mandi',
        'Shimla', 'Sirmaur', 'Solan', 'Una',
      ],
    ),
    StateUT(
      name: 'Jharkhand',
      type: 'State',
      districts: [
        'Bokaro', 'Chatra', 'Deoghar', 'Dhanbad', 'Dumka', 'East Singhbhum', 'Garhwa', 'Giridih',
        'Godda', 'Gumla', 'Hazaribagh', 'Jamtara', 'Khunti', 'Koderma', 'Latehar', 'Lohardaga',
        'Pakur', 'Palamu', 'Ramgarh', 'Ranchi', 'Sahebganj', 'Seraikela Kharsawan', 'Simdega', 'West Singhbhum',
      ],
    ),
    StateUT(
      name: 'Karnataka',
      type: 'State',
      districts: [
        'Bagalkote', 'Ballari', 'Belagavi', 'Bengaluru Rural', 'Bengaluru Urban', 'Bidar', 'Chamarajanagara',
        'Chikkaballapura', 'Chikkamagaluru', 'Chitradurga', 'Dakshina Kannada', 'Davangere', 'Dharwad',
        'Gadag', 'Hassan', 'Haveri', 'Kalaburagi', 'Kodagu', 'Kolar', 'Koppal', 'Mandya', 'Mysuru',
        'Raichur', 'Ramanagara', 'Shivamogga', 'Tumakuru', 'Udupi', 'Uttara Kannada', 'Vijayanagara',
        'Vijayapura', 'Yadgir',
      ],
    ),
    StateUT(
      name: 'Kerala',
      type: 'State',
      districts: [
        'Alappuzha', 'Ernakulam', 'Idukki', 'Kannur', 'Kasaragod', 'Kollam', 'Kottayam', 'Kozhikode',
        'Malappuram', 'Palakkad', 'Pathanamthitta', 'Thiruvananthapuram', 'Thrissur', 'Wayanad',
      ],
    ),
    StateUT(
      name: 'Madhya Pradesh',
      type: 'State',
      districts: [
        'Agar Malwa', 'Alirajpur', 'Anuppur', 'Ashoknagar', 'Balaghat', 'Barwani', 'Betul', 'Bhind',
        'Bhopal', 'Burhanpur', 'Chhatarpur', 'Chhindwara', 'Damoh', 'Datia', 'Dewas', 'Dhar', 'Dindori',
        'Guna', 'Gwalior', 'Harda', 'Hoshangabad', 'Indore', 'Jabalpur', 'Jhabua', 'Katni', 'Khandwa',
        'Khargone', 'Mandla', 'Mandsaur', 'Morena', 'Narsinghpur', 'Neemuch', 'Niwari', 'Panna', 'Raisen',
        'Rajgarh', 'Ratlam', 'Rewa', 'Sagar', 'Satna', 'Sehore', 'Seoni', 'Shahdol', 'Shajapur',
        'Sheopur', 'Shivpuri', 'Sidhi', 'Singrauli', 'Tikamgarh', 'Ujjain', 'Umaria', 'Vidisha',
      ],
    ),
    StateUT(
      name: 'Maharashtra',
      type: 'State',
      districts: [
        'Ahmednagar', 'Akola', 'Amravati', 'Chhatrapati Sambhaji Nagar', 'Bhandara', 'Beed', 'Buldhana',
        'Chandrapur', 'Dhule', 'Gadchiroli', 'Gondia', 'Hingoli', 'Jalgaon', 'Jalna', 'Kolhapur',
        'Latur', 'Mumbai City', 'Mumbai Suburban', 'Nagpur', 'Nanded', 'Nandurbar', 'Nashik',
        'Dharashiv', 'Palghar', 'Parbhani', 'Pune', 'Raigad', 'Ratnagiri', 'Sangli', 'Satara',
        'Sindhudurg', 'Solapur', 'Thane', 'Wardha', 'Washim', 'Yavatmal',
      ],
    ),
    StateUT(
      name: 'Manipur',
      type: 'State',
      districts: [
        'Bishnupur', 'Chandel', 'Churachandpur', 'Imphal East', 'Imphal West', 'Jiribam', 'Kakching',
        'Kamjong', 'Kangpokpi', 'Noney', 'Pherzawl', 'Senapati', 'Tamenglong', 'Tengnoupal', 'Thoubal', 'Ukhrul',
      ],
    ),
    StateUT(
      name: 'Meghalaya',
      type: 'State',
      districts: [
        'Eastern West Khasi Hills', 'East Garo Hills', 'East Jaintia Hills', 'East Khasi Hills',
        'North Garo Hills', 'Ri Bhoi', 'South Garo Hills', 'South West Garo Hills',
        'South West Khasi Hills', 'West Garo Hills', 'West Jaintia Hills', 'West Khasi Hills',
      ],
    ),
    StateUT(
      name: 'Mizoram',
      type: 'State',
      districts: [
        'Aizawl', 'Champhai', 'Hnahthial', 'Khawzawl', 'Kolasib', 'Lawngtlai', 'Lunglei', 'Mamit',
        'Saitual', 'Serchhip', 'Siaha',
      ],
    ),
    StateUT(
      name: 'Nagaland',
      type: 'State',
      districts: [
        'Chümoukedima', 'Dimapur', 'Kiphire', 'Kohima', 'Longleng', 'Mokokchung', 'Mon', 'Niuland',
        'Noklak', 'Peren', 'Phek', 'Shamator', 'Tseminyü', 'Tuensang', 'Wokha', 'Zünheboto',
      ],
    ),
    StateUT(
      name: 'Odisha',
      type: 'State',
      districts: [
        'Angul', 'Balangir', 'Balasore', 'Bargarh', 'Bhadrak', 'Boudh', 'Cuttack', 'Deogarh', 'Dhenkanal',
        'Gajapati', 'Ganjam', 'Jagatsinghpur', 'Jajpur', 'Jharsuguda', 'Kalahandi', 'Kandhamal',
        'Kendrapara', 'Kendujhar', 'Khordha', 'Koraput', 'Malkangiri', 'Mayurbhanj', 'Nabarangpur',
        'Nayagarh', 'Nuapada', 'Puri', 'Rayagada', 'Sambalpur', 'Subarnapur', 'Sundargarh',
      ],
    ),
    StateUT(
      name: 'Punjab',
      type: 'State',
      districts: [
        'Amritsar', 'Barnala', 'Bathinda', 'Faridkot', 'Fatehgarh Sahib', 'Fazilka', 'Ferozepur',
        'Gurdaspur', 'Hoshiarpur', 'Jalandhar', 'Kapurthala', 'Ludhiana', 'Malerkotla', 'Mansa',
        'Moga', 'Muktsar', 'Pathankot', 'Patiala', 'Rupnagar', 'Sahibzada Ajit Singh Nagar',
        'Shaheed Bhagat Singh Nagar', 'Sangrur', 'Tarn Taran',
      ],
    ),
    StateUT(
      name: 'Rajasthan',
      type: 'State',
      districts: [
        'Ajmer', 'Alwar', 'Anupgarh', 'Balotra', 'Banswara', 'Baran', 'Barmer', 'Beawar', 'Bharatpur',
        'Bhilwara', 'Bikaner', 'Bundi', 'Chittorgarh', 'Churu', 'Dausa', 'Deeg', 'Didwana-Kuchaman',
        'Dholpur', 'Dudu', 'Dungarpur', 'Ganganagar', 'Gangapur City', 'Hanumangarh', 'Jaipur',
        'Jaipur Rural', 'Jaisalmer', 'Jalore', 'Jhalawar', 'Jhunjhunu', 'Jodhpur', 'Jodhpur Rural',
        'Karauli', 'Kekri', 'Khairthal-Tijara', 'Kota', 'Kotputli-Behror', 'Nagaur', 'Neem Ka Thana',
        'Pali', 'Phalodi', 'Pratapgarh', 'Rajsamand', 'Salumbar', 'Sanchore', 'Sawai Madhopur',
        'Shahpura', 'Sikar', 'Sirohi', 'Tonk', 'Udaipur',
      ],
    ),
    StateUT(
      name: 'Sikkim',
      type: 'State',
      districts: ['Gangtok', 'Gyalshing', 'Pakyong', 'Namchi', 'Mangan', 'Soreng'],
    ),
    StateUT(
      name: 'Tamil Nadu',
      type: 'State',
      districts: [
        'Ariyalur', 'Chengalpattu', 'Chennai', 'Coimbatore', 'Cuddalore', 'Dharmapuri', 'Dindigul',
        'Erode', 'Kallakurichi', 'Kancheepuram', 'Karur', 'Krishnagiri', 'Madurai', 'Mayiladuthurai',
        'Nagapattinam', 'Kanniyakumari', 'Namakkal', 'Perambalur', 'Pudukkottai', 'Ramanathapuram',
        'Ranipet', 'Salem', 'Sivaganga', 'Tenkasi', 'Thanjavur', 'Theni', 'Thoothukudi', 'Tiruchirappalli',
        'Tirunelveli', 'Tirupathur', 'Tiruppur', 'Tiruvallur', 'Tiruvannamalai', 'Tiruvarur', 'Vellore',
        'Viluppuram', 'Virudhunagar', 'Nilgiris',
      ],
    ),
    StateUT(
      name: 'Telangana',
      type: 'State',
      districts: [
        'Adilabad', 'Bhadradri Kothagudem', 'Hanumakonda', 'Hyderabad', 'Jagtial', 'Jangaon',
        'Jayashankar Bhupalpally', 'Jogulamba Gadwal', 'Kamareddy', 'Karimnagar', 'Khammam',
        'Kumuram Bheem Asifabad', 'Mahabubabad', 'Mahbubnagar', 'Mancherial', 'Medak', 'Medchal-Malkajgiri',
        'Mulugu', 'Nagarkurnool', 'Nalgonda', 'Narayanpet', 'Nirmal', 'Nizamabad', 'Peddapalli',
        'Rajanna Sircilla', 'Ranga Reddy', 'Sangareddy', 'Siddipet', 'Suryapet', 'Vikarabad',
        'Wanaparthy', 'Warangal', 'Yadadri Bhuvanagiri',
      ],
    ),
    StateUT(
      name: 'Tripura',
      type: 'State',
      districts: [
        'Dhalai', 'Gomati', 'Khowai', 'North Tripura', 'Sepahijala', 'South Tripura', 'Unakoti', 'West Tripura',
      ],
    ),
    StateUT(
      name: 'Uttar Pradesh',
      type: 'State',
      districts: [
        'Agra', 'Aligarh', 'Ambedkar Nagar', 'Amethi', 'Amroha', 'Auraiya', 'Ayodhya', 'Azamgarh',
        'Baghpat', 'Bahraich', 'Ballia', 'Balrampur', 'Banda', 'Barabanki', 'Bareilly', 'Basti',
        'Bhadohi', 'Bijnor', 'Budaun', 'Bulandshahr', 'Chandauli', 'Chitrakoot', 'Deoria', 'Etah',
        'Etawah', 'Farrukhabad', 'Fatehpur', 'Firozabad', 'Gautam Buddha Nagar', 'Ghaziabad', 'Ghazipur',
        'Gonda', 'Gorakhpur', 'Hamirpur', 'Hapur', 'Hardoi', 'Hathras', 'Jalaun', 'Jaunpur', 'Jhansi',
        'Kannauj', 'Kanpur Dehat', 'Kanpur Nagar', 'Kasganj', 'Kaushambi', 'Kheri', 'Kushinagar',
        'Lalitpur', 'Lucknow', 'Maharajganj', 'Mahoba', 'Mainpuri', 'Mathura', 'Mau', 'Meerut',
        'Mirzapur', 'Moradabad', 'Muzaffarnagar', 'Pilibhit', 'Pratapgarh', 'Prayagraj', 'Raebareli',
        'Rampur', 'Saharanpur', 'Sambhal', 'Sant Kabir Nagar', 'Shahjahanpur', 'Shamli', 'Shravasti',
        'Siddharthnagar', 'Sitapur', 'Sonbhadra', 'Sultanpur', 'Unnao', 'Varanasi',
      ],
    ),
    StateUT(
      name: 'Uttarakhand',
      type: 'State',
      districts: [
        'Almora', 'Bageshwar', 'Chamoli', 'Champawat', 'Dehradun', 'Haridwar', 'Nainital', 'Pauri Garhwal',
        'Pithoragarh', 'Rudraprayag', 'Tehri Garhwal', 'Udham Singh Nagar', 'Uttarkashi',
      ],
    ),
    StateUT(
      name: 'West Bengal',
      type: 'State',
      districts: [
        'Alipurduar', 'Bankura', 'Birbhum', 'Cooch Behar', 'Dakshin Dinajpur', 'Darjeeling', 'Hooghly',
        'Howrah', 'Jalpaiguri', 'Jhargram', 'Kalimpong', 'Kolkata', 'Malda', 'Murshidabad', 'Nadia',
        'North 24 Parganas', 'Paschim Bardhaman', 'Paschim Medinipur', 'Purba Bardhaman', 'Purba Medinipur',
        'Purulia', 'South 24 Parganas', 'Uttar Dinajpur',
      ],
    ),

    // --- 8 UNION TERRITORIES ---
    StateUT(
      name: 'Andaman and Nicobar Islands',
      type: 'UT',
      districts: ['Nicobar', 'North and Middle Andaman', 'South Andaman'],
    ),
    StateUT(
      name: 'Chandigarh',
      type: 'UT',
      districts: ['Chandigarh'],
    ),
    StateUT(
      name: 'Dadra and Nagar Haveli and Daman and Diu',
      type: 'UT',
      districts: ['Dadra and Nagar Haveli', 'Daman', 'Diu'],
    ),
    StateUT(
      name: 'Delhi NCR',
      type: 'UT',
      districts: [
        'Central Delhi', 'East Delhi', 'New Delhi', 'North Delhi', 'North East Delhi',
        'North West Delhi', 'Shahdara', 'South Delhi', 'South East Delhi', 'South West Delhi', 'West Delhi',
      ],
    ),
    StateUT(
      name: 'Jammu and Kashmir',
      type: 'UT',
      districts: [
        'Anantnag', 'Bandipora', 'Baramulla', 'Budgam', 'Doda', 'Ganderbal', 'Jammu', 'Kathua',
        'Kishtwar', 'Kulgam', 'Kupwara', 'Poonch', 'Pulwama', 'Rajouri', 'Ramban', 'Reasi',
        'Samba', 'Shopian', 'Srinagar', 'Udhampur',
      ],
    ),
    StateUT(
      name: 'Ladakh',
      type: 'UT',
      districts: ['Kargil', 'Leh'],
    ),
    StateUT(
      name: 'Lakshadweep',
      type: 'UT',
      districts: ['Lakshadweep'],
    ),
    StateUT(
      name: 'Puducherry',
      type: 'UT',
      districts: ['Karaikal', 'Mahe', 'Puducherry', 'Yanam'],
    ),
  ];

  static List<String> get states =>
      all.where((e) => e.type == 'State').map((e) => e.name).toList();

  static List<String> get unionTerritories =>
      all.where((e) => e.type == 'UT').map((e) => e.name).toList();

  static List<String> getDistrictsFor(String? stateName) {
    if (stateName == null || stateName.isEmpty) return const [];
    try {
      final entry = all.firstWhere(
        (e) => e.name.toLowerCase() == stateName.toLowerCase(),
      );
      return entry.districts;
    } catch (_) {
      return const [];
    }
  }

  static bool isValidDistrict(String? stateName, String? district) {
    if (stateName == null || district == null) return false;
    final districts = getDistrictsFor(stateName);
    return districts.any((d) => d.toLowerCase() == district.toLowerCase());
  }
}
