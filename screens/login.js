import React from 'react';
import { StyleSheet, Text, View, Image, Button} from 'react-native';
import { AppLoading } from 'expo';
import * as Font from 'expo-font';
import { TextInput, TouchableOpacity } from 'react-native-gesture-handler';
import DropDownPicker from 'react-native-dropdown-picker';
import { Camera } from 'expo-camera';

let customFonts  = {
    'FuturaH': require('../assets/fonts/futurah.ttf'),
    'FuturaL': require('../assets/fonts/futural.ttf'),
  };
  var imgdata=null;
  var url=null;
  var cUrl=null;
  var pUrl=null;
export default class Reg extends React.Component  {
  state = {
    fontsLoaded: false,
    method: '',
    imageCaptured: false,
  };

  async _loadFontsAsync() {
    await Font.loadAsync(customFonts);
    this.setState({ fontsLoaded: true });
  }

  componentDidMount() {
    this._loadFontsAsync();
    
  }

  registerUser(){
    fetch('https://us-central1-aiot-fit-xlab.cloudfunctions.net/autoplaygeneral', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        },
        body: JSON.stringify({"action": "register", "lat" : 2.2222, "lon": 45.225, "email":"e@mail.com", "password" : "somepasswordhere", "spotify": "2222222"})
})
    .then((response) => response.json())
    .then((responseJson) => {
console.log(responseJson);
    })
    .catch((error) => {
        console.error(error);
    });
  }

  render(){
    const { hasCameraPermission } = this.state;
    const { isRecording, isFetching } = this.state;
    const {ref} = this.state;
    let { image } = this.state;
    const takePicture = async () => {
            console.log('Captured')
            const options = {quality: 0.5, base64: true};
            imgdata = await this.camera.takePictureAsync(options);
            url=imgdata.uri;
            console.log('Image Captured');
            console.log(url);
            this.setState({imageCaptured:true})
            let base64Img = `data:image/jpg;base64,${imgdata.base64}`
      
            
           let cloudinary = 'https://api.cloudinary.com/v1_1/diywehkap/image/upload';
        
            let data = {
              "file": base64Img,
              "upload_preset": "hm4fkyir",
            }
            fetch(cloudinary, {
              body: JSON.stringify(data),
              headers: {
                'content-type': 'application/json'
              },
              method: 'POST',
            }).then(async r => {
              let data = await r.json()
              cUrl=data.secure_url;
              pUrl=cUrl.toString();
              console.log(pUrl);
              return pUrl
          }).catch(err=>console.log(err));
        }
    if (this.state.fontsLoaded) {
    return (
    <View style={styles.container}>
     
      <Text style={{position:'relative',fontSize:60,marginTop:'20%', textAlign:'center', color:'#364f6b', fontFamily:'FuturaH'}}>Login</Text>
      <DropDownPicker
      placeholder="Select a primary authentication method"
    items={[
        {label: 'Face Recognition', value: 'face'},
        {label: 'Facial Expression', value: 'expression'},
        {label: 'Hand gesture', value: 'hand'},
        {label: 'Voice Password', value: 'voice'},
    ]}
    defaultValue={this.state.method}
    containerStyle={{height: 40, width:'70%', alignSelf:'center', marginTop:'5%'}}
    style={{backgroundColor: '#fafafa'}}
    itemStyle={{
        justifyContent: 'flex-start'
    }}
    dropDownStyle={{backgroundColor: '#fafafa'}}
    onChangeItem={item => {
      this.setState({
        method: item.value
    });
    console.log(this.state.method)
    }}
/>
      <TextInput placeholder='Email' style={{position:'relative',fontSize:20,margin:'auto', paddingLeft:'5%', color:'#798497', fontFamily:'FuturaL', marginTop:'5%', backgroundColor:'#EAEAEA',padding:'2.5%', width:'80%', borderRadius:5,alignSelf:'center'}}></TextInput>
      <TextInput placeholder='Password' secureTextEntry={true} style={{position:'relative',fontSize:20,margin:'auto', paddingLeft:'5%', color:'#798497', fontFamily:'FuturaL', marginTop:'5%', backgroundColor:'#EAEAEA',padding:'2.5%', width:'80%', borderRadius:5,alignSelf:'center'}}></TextInput>
      

     
   
      
      {this.state.imageCaptured && <Text style={{position:'relative',fontSize:20,margin:'auto', textAlign:'center', color:'#FFF', fontFamily:'FuturaH', marginTop:'15%', backgroundColor:'#ED008C', padding:'5%', width:'70%', borderRadius:10, alignSelf:'center', elevation:1}} onPress={()=>{this.props.navigation.navigate('Msg');}}>LOGIN</Text>}
      <Text style={{position:'relative',fontSize:15,margin:'auto', textAlign:'center', color:'#2D3748', fontFamily:'FuturaL', marginTop:'5%',alignSelf:'center'}} onPress={()=>this.props.navigation.navigate('Reg')}>Don't have an account yet? Sign up</Text>
      {this.state.method!='' && !this.state.imageCaptured &&
 <Camera style={{ flex: 0.5, position:'absolute', height:500, width:400, marginTop:'70%', zIndex:6 }} type={this.state.type} ref={ref => {this.camera = ref;}}>
 <View
   style={{
     flex: 1,
     backgroundColor: 'transparent',
     flexDirection: 'row',
   }}>
   <TouchableOpacity
     style={{
       flex: 0.1,
       alignSelf: 'flex-end',
       alignItems: 'center',
     }}
     onPress={() => {
       this.setState({
         type:
           this.state.type === Camera.Constants.Type.back
             ? Camera.Constants.Type.front
             : Camera.Constants.Type.back,
       });
     }}>
     <Text style={{ fontSize: 18, marginBottom: 10, color: 'white' }}> Flip </Text>
   </TouchableOpacity>
   <Text style={{position:'relative',fontSize:20,margin:'auto', textAlign:'center', color:'#FFF', fontFamily:'FuturaH', marginTop:'90%', backgroundColor:'#ED008C', padding:'5%', width:'70%', borderRadius:10, alignSelf:'center', elevation:1}} onPress={()=>{takePicture();}}>CAPTURE</Text>
 </View>
</Camera>}
    </View>
    );
    }
    else {
    return <AppLoading />;
    }
  }
}

const styles = StyleSheet.create({
  container: {
    height:'100%',
    position:'relative',
    
  },
  header:{
    height:'30%',
    width:'70%',
    marginTop:'20%',
    resizeMode:'contain',
    alignSelf:'center'
  },
  
});